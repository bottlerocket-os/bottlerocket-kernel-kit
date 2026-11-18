/*!
# NVIDIA MIG Manager
`nvidia-migmanager` ensures that MIG settings are applied to an instance that supports
it. It is called by `nvidia-migmanager.service`.

The binary reads its config file and based on the config, it activates/deactivates MIG
and applies the profile according to the type of GPU present in the instance.

NVIDIA MIG is currently supported only in A30, A100, H100 and H200 GPUs.

## Example:
```toml
[settings.kubelet-device-plugins.nvidia]
device-partitioning-strategy="mig"

[settings.kubelet-device-plugins.nvidia.mig.profile]
"a100.40gb"="2"
"h100.80gb"="4"
"h200.141gb"="3"
```
This would partition the GPUs in an instance with A100 GPU into 2 parts, instance with H100
into 4 parts and instance with H200 into 3 parts.
*/

mod mig_profile;

use crate::mig_profile::*;
use argh::FromArgs;
use log::{info, trace, warn};
use regex::Regex;
use serde::Deserialize;
use simplelog::{Config as LogConfig, LevelFilter, SimpleLogger};
use snafu::{ensure, ResultExt};
use std::cmp::min;
use std::collections::HashMap;
use std::ffi::OsStr;
use std::fs;
use std::path::Path;
use std::process::{self, Command};
use std::thread;
use std::time::Duration;

const NVIDIA_VENDOR_ID: &str = "10DE";

const DEFAULT_CONFIG_PATH: &str = "/etc/nvidia-migmanager/nvidia-migmanager.toml";
const NVIDIA_SMI_PATH: &str = "/usr/bin/nvidia-smi";
const SYSTEMCTL_PATH: &str = "/usr/bin/systemctl";
const REBOOT_REQUIRED_MARKER_FILE: &str = "/run/nvidia-migmanager/reboot-required";

const GPU_MODEL_REGEX: &str = r"[A-Za-z]\d+\.(\d+)gb";
const MIG_PROFILE_REGEX: &str = r"(\d+)g\.(\d+)gb";

/// Stores arguments
#[derive(FromArgs, PartialEq, Debug)]
struct Args {
    /// log-level trace|debug|info|warn|error
    #[argh(option)]
    log_level: Option<LevelFilter>,
    /// configuration file with the desired MIG settings
    #[argh(option, default = "DEFAULT_CONFIG_PATH.to_string()", short = 'd')]
    config_path: String,
    #[argh(subcommand)]
    subcommand: Subcommand,
}

/// Stores the subcommand to be executed
#[derive(FromArgs, Debug, PartialEq)]
#[argh(subcommand)]
enum Subcommand {
    HandleMigManager(HandleMigManagerArgs),
    RebootIfRequired(RebootIfRequiredArgs),
}

#[derive(FromArgs, PartialEq, Debug)]
#[argh(subcommand, name = "reboot-if-required")]
/// Reboot the host if reboot-to-reconcile is set and the boot settings changed
struct RebootIfRequiredArgs {}

/// Handles logic to apply MIG
#[derive(FromArgs, Debug, PartialEq)]
#[argh(subcommand, name = "apply-mig")]
struct HandleMigManagerArgs {}

#[derive(Debug, PartialEq, Deserialize)]
#[serde(rename_all = "kebab-case")]
struct NvidiaMigConfig {
    #[serde(default)]
    device_partitioning_strategy: String,
    #[serde(default)]
    profile: HashMap<String, String>,
}

#[derive(Debug, PartialEq, Clone)]
enum NvidiaGpu {
    A100_40GB,
    A100_80GB,
    H100_80GB,
    H200_141GB,
    B200_180GB,
    B300_269GB,
    RtxPro6000_96GB,
    RtxPro4500_32GB,
    Other,
}

impl NvidiaGpu {
    fn is_ampere(&self) -> bool {
        use NvidiaGpu::*;
        matches!(self, A100_40GB | A100_80GB)
    }
}

#[derive(Hash, Debug, Clone, PartialEq, Eq)]
enum MigState {
    Unsupported,
    Enabled,
    Disabled,
    Transition,
    Unknown,
}

impl MigState {
    fn is_disabled(&self) -> bool {
        matches!(self, MigState::Disabled)
    }

    fn is_enabled(&self) -> bool {
        matches!(self, MigState::Enabled)
    }

    fn is_unsupported(&self) -> bool {
        matches!(self, MigState::Unsupported)
    }
}

struct MigGpu {
    model: NvidiaGpu,
    state: MigState,
}

/// Wrapper around process::Command that adds error checking.
fn command<I, S>(bin_path: &str, args: I) -> Result<String>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    let mut command = Command::new(bin_path);
    command.args(args);
    let output = command
        .output()
        .context(error::ExecutionFailureSnafu { command })?;

    trace!("stdout: {}", String::from_utf8_lossy(&output.stdout));
    trace!("stderr: {}", String::from_utf8_lossy(&output.stderr));

    ensure!(
        output.status.success(),
        error::CommandFailureSnafu { bin_path, output }
    );

    let output_str = String::from_utf8_lossy(&output.stdout);

    Ok(output_str.to_string())
}

// Runs the nvidia-smi command to enable/disable MIG in all GPUs
fn set_mig_mode(mig_enabled: bool) -> Result<()> {
    info!(
        "{} MIG.",
        if mig_enabled { "Enabling" } else { "Disabling" }
    );

    command(NVIDIA_SMI_PATH, ["-mig", &(mig_enabled as u8).to_string()])?;

    Ok(())
}

// Runs the nvidia-smi command to apply the correct MIG profile in all the GPUs
fn set_mig_profile(profile_string: &str) -> Result<()> {
    info!("Activating MIG profile ...");

    command(NVIDIA_SMI_PATH, ["mig", "-cgi", profile_string, "-C"])?;

    Ok(())
}

// Uses pci-device id to find out the GPU model of the instance
fn get_gpu_model(pci_device_id: &str) -> Result<NvidiaGpu> {
    ensure!(
        pci_device_id.ends_with(NVIDIA_VENDOR_ID),
        error::GpuModelSnafu
    );

    if pci_device_id.starts_with("0x20B0") {
        info!("Found NVIDIA A100-40GB GPU.");
        Ok(NvidiaGpu::A100_40GB)
    } else if pci_device_id.starts_with("0x20B2") || pci_device_id.starts_with("0x20B5") {
        info!("Found NVIDIA A100-80GB GPU.");
        Ok(NvidiaGpu::A100_80GB)
    } else if pci_device_id.starts_with("0x2330")
        || pci_device_id.starts_with("0x2321")
        || pci_device_id.starts_with("0x2331")
        || pci_device_id.starts_with("0x2339")
    {
        info!("Found NVIDIA H100-80GB GPU.");
        Ok(NvidiaGpu::H100_80GB)
    } else if pci_device_id.starts_with("0x2335")
        || pci_device_id.starts_with("0x233B")
        || pci_device_id.starts_with("0x2348")
    {
        info!("Found NVIDIA H200-141GB GPU.");
        Ok(NvidiaGpu::H200_141GB)
    } else if pci_device_id.starts_with("0x2901") || pci_device_id.starts_with("0x2941") {
        info!("Found NVIDIA B200-180GB GPU.");
        Ok(NvidiaGpu::B200_180GB)
    } else if pci_device_id.starts_with("0x2BB5") {
        info!("Found NVIDIA RTX PRO 6000 Blackwell GPU.");
        Ok(NvidiaGpu::RtxPro6000_96GB)
    } else if pci_device_id.starts_with("0x2C3A") {
        info!("Found NVIDIA RTX PRO 4500 Blackwell GPU.");
        Ok(NvidiaGpu::RtxPro4500_32GB)
    } else if pci_device_id.starts_with("0x3182") {
        info!("Found NVIDIA B300-269GB GPU.");
        Ok(NvidiaGpu::B300_269GB)
    } else {
        warn!("Found NVIDIA Device but couldn't confirm variant.");
        Ok(NvidiaGpu::Other)
    }
}

fn get_gpu_state(current_state: &str, next_state: &str) -> MigState {
    let mut gpu_state = MigState::Unknown;

    if current_state != next_state {
        gpu_state = MigState::Transition;
    } else if current_state == "Enabled" {
        gpu_state = MigState::Enabled;
    } else if current_state == "Disabled" {
        gpu_state = MigState::Disabled;
    } else if current_state == "[N/A]" {
        gpu_state = MigState::Unsupported;
    }

    gpu_state
}

// Runs nvidia-smi command to find out the current state of the Nvidia GPU.
fn get_gpu_info() -> Result<Vec<MigGpu>> {
    info!("Fetching GPU devices data ...");

    let output = command(
        NVIDIA_SMI_PATH,
        [
            "--query-gpu=pci.device_id,mig.mode.current,mig.mode.pending",
            "--format=csv,noheader",
        ],
    )?;

    let mut gpu_info = Vec::new();

    for row in output.lines() {
        let parts: Vec<_> = row.split(", ").collect();

        ensure!(parts.len() == 3, error::NvidiaSmiSnafu);

        let gpu_model = get_gpu_model(parts[0])?;
        let gpu_state = get_gpu_state(parts[1], parts[2]);

        let gpu = MigGpu {
            model: gpu_model,
            state: gpu_state,
        };
        gpu_info.push(gpu);
    }

    Ok(gpu_info)
}

/// Read the config file to get MIG settings
fn get_mig_settings<P>(config_path: P) -> Result<NvidiaMigConfig>
where
    P: AsRef<Path>,
{
    let config_str = fs::read_to_string(config_path.as_ref()).context(error::ReadConfigSnafu {
        config_path: config_path.as_ref(),
    })?;

    let config: NvidiaMigConfig =
        toml::from_str(&config_str).context(error::TomlDeserializationSnafu {
            config_path: config_path.as_ref(),
        })?;

    Ok(config)
}

fn process_mig_config<T>(model_str: &str, mig_settings: &NvidiaMigConfig) -> Result<()>
where
    T: MigGpuProfile,
{
    let default_profile = "1".to_string();
    let gpu_model = model_str.to_string();
    let mig_profile = mig_settings
        .profile
        .get(&gpu_model)
        .unwrap_or(&default_profile);

    info!("MIG Profile or the number of GPU slices: {:?}", mig_profile);
    let profile =
        serde_plain::from_str::<T>(mig_profile.as_str()).context(error::DeserializationSnafu)?;

    set_mig_profile(profile.get_mig_profile())
}

fn process_unknown_gpu_mig_config(gpu: &str, mig_profile: &str) -> Result<()> {
    // If the GPU is unknown, we want the exact MIG Profile and not the number of slices.
    ensure!(mig_profile.len() > 1, error::MigProfileSnafu {});

    // The GPU and MIG Profile here are expected in a deterministic format and enforced in
    // settings API. We parse this to form the MIG profile string using known GPU hardware constraints.
    let gpu_regex = Regex::new(GPU_MODEL_REGEX).unwrap();
    let profile_regex = Regex::new(MIG_PROFILE_REGEX).unwrap();

    let gpu_ram: usize = gpu_regex
        .captures(gpu)
        .map(|captures| captures[1].parse().unwrap_or(0))
        .unwrap();
    let (compute_slices, slice_ram) = profile_regex
        .captures(mig_profile)
        .map(|captures| {
            (
                captures[1].parse().unwrap_or(0),
                captures[2].parse().unwrap_or(0),
            )
        })
        .unwrap();

    // Prevents unsafe division below and enforces logical limits to RAM and compute slices
    ensure!(
        gpu_ram > 0 && slice_ram > 0 && compute_slices > 0,
        error::MigProfileSnafu {}
    );

    // There are total 7 compute slices in a MIG supported GPU. So, total
    // number of partitions of the GPU will be minimum of
    // 7/(compute slices in each partition) and (total VRAM / VRAM of each partition)
    let num_slices: usize = min(gpu_ram / slice_ram, 7 / compute_slices);
    let profile_string = std::iter::repeat_n(mig_profile, num_slices)
        .collect::<Vec<_>>()
        .join(",");

    set_mig_profile(profile_string.as_str())
}

fn get_instance_gpu(gpu_info: &[MigGpu]) -> Result<NvidiaGpu> {
    let reference_gpu_model = gpu_info.first().unwrap().model.clone();
    ensure!(
        gpu_info.iter().all(|gpu| gpu.model == reference_gpu_model),
        error::MigGpuSnafu
    );

    Ok(reference_gpu_model)
}

fn enable_mig(mig_settings: NvidiaMigConfig, gpu_info: &[MigGpu]) -> Result<()> {
    ensure!(!gpu_info.is_empty(), error::GpuModelSnafu);

    let (is_ampere_gpu_present, has_disabled_mig, is_mig_unsupported) = gpu_info.iter().fold(
        (false, false, false),
        |(ampere, disabled, unsupported), gpu| {
            (
                ampere || gpu.model.is_ampere(),
                disabled || gpu.state.is_disabled(),
                unsupported || gpu.state.is_unsupported(),
            )
        },
    );

    if is_mig_unsupported {
        warn!("MIG is not supported by the available NVIDIA GPU.");
        return Ok(());
    }

    if has_disabled_mig {
        // Enable MIG for all the GPU
        set_mig_mode(true)?;

        // If any GPU is A100 create marker file for reboot to reconcile
        // for the gpu reset and move from transitional state to enabled
        if is_ampere_gpu_present {
            info!("Rebooting to apply MIG Settings...");
            std::fs::write(REBOOT_REQUIRED_MARKER_FILE, "Enabling MIG").context(
                error::WriteMarkerSnafu {
                    marker_path: REBOOT_REQUIRED_MARKER_FILE,
                },
            )?;

            return Ok(());
        }
    }

    match get_instance_gpu(gpu_info) {
        Ok(NvidiaGpu::A100_40GB) => {
            process_mig_config::<NvidiaA100_40gbMigProfile>("a100.40gb", &mig_settings)
        }
        Ok(NvidiaGpu::A100_80GB) => {
            process_mig_config::<NvidiaA100_80gbMigProfile>("a100.80gb", &mig_settings)
        }
        Ok(NvidiaGpu::H100_80GB) => {
            process_mig_config::<NvidiaH100_80gbMigProfile>("h100.80gb", &mig_settings)
        }
        Ok(NvidiaGpu::H200_141GB) => {
            process_mig_config::<NvidiaH200_141gbMigProfile>("h200.141gb", &mig_settings)
        }
        Ok(NvidiaGpu::B200_180GB) => {
            process_mig_config::<NvidiaB200_180gbMigProfile>("b200.180gb", &mig_settings)
        }
        Ok(NvidiaGpu::RtxPro6000_96GB) => {
            process_mig_config::<NvidiaRtxPro6000_96gbMigProfile>("rtxpro6000.96gb", &mig_settings)
        }
        Ok(NvidiaGpu::RtxPro4500_32GB) => {
            process_mig_config::<NvidiaRtxPro4500_32gbMigProfile>("rtxpro4500.32gb", &mig_settings)
        }
        Ok(NvidiaGpu::B300_269GB) => {
            process_mig_config::<NvidiaB300_269gbMigProfile>("b300.269gb", &mig_settings)
        }
        _ => {
            let known_gpus: Vec<&str> = vec![
                "a100.40gb",
                "a100.80gb",
                "h100.80gb",
                "h200.141gb",
                "b200.180gb",
                "rtxpro6000.96gb",
                "rtxpro4500.32gb",
            ];
            let mut filtered_map = mig_settings.profile;
            filtered_map.retain(|key, _| !known_gpus.contains(&key.as_str()));

            let mut entries: Vec<_> = filtered_map.into_iter().collect();
            entries.sort_by(|gpu, mig_profile| gpu.0.cmp(&mig_profile.0));

            // The GPU in the current instance is not one of the known GPUs. We attempt using the profiles that doesn't belong to one of the known GPUs.
            for (gpu, mig_profile) in entries {
                match process_unknown_gpu_mig_config(&gpu, &mig_profile) {
                    Ok(()) => {
                        info!("Successfully applied MIG Profile: {}", mig_profile);
                        return Ok(());
                    }
                    Err(_) => {
                        warn!(
                            "The Profile {} is not a valid MIG Profile for the given GPU.",
                            mig_profile
                        );
                        continue;
                    }
                }
            }

            Ok(())
        }
    }
}

fn disable_mig(gpu_info: &[MigGpu]) -> Result<()> {
    let (is_ampere_gpu_present, has_enabled_mig) =
        gpu_info
            .iter()
            .fold((false, false), |(ampere, enabled), gpu| {
                (
                    ampere || gpu.model.is_ampere(),
                    enabled || gpu.state.is_enabled(),
                )
            });

    if has_enabled_mig {
        // Disable MIG for the GPU
        set_mig_mode(false)?;

        // If GPU is A100 create marker file for reboot to reconcile
        // for the gpu reset and move from transitional state to disabled
        if is_ampere_gpu_present {
            info!("Rebooting to apply MIG Settings...");
            std::fs::write(REBOOT_REQUIRED_MARKER_FILE, "Disabling MIG").context(
                error::WriteMarkerSnafu {
                    marker_path: REBOOT_REQUIRED_MARKER_FILE,
                },
            )?;
        }
    }

    Ok(())
}

fn handle_mig_manager(mig_settings: NvidiaMigConfig, gpu_info: &[MigGpu]) -> Result<()> {
    if mig_settings.device_partitioning_strategy == "mig" {
        enable_mig(mig_settings, gpu_info)
    } else {
        disable_mig(gpu_info)
    }
}

fn reboot_if_required() -> Result<()> {
    let reboot_required = Path::new(REBOOT_REQUIRED_MARKER_FILE).exists();

    if reboot_required {
        info!("GPU reset is required to apply MIG Settings. Initiating reboot...");
        command(SYSTEMCTL_PATH, ["reboot"])?;
        // The "systemctl reboot" process will not block until the host does
        // reboot, but return as soon as the request either failed or the job
        // to start the systemd reboot.target and its dependencies have been
        // enqueued. As the shutdown.target that is being pulled in conflicts
        // with most anything else, the other jobs needed to boot the host
        // will be cancelled and the boot will not proceed.
        //
        // The above is subtle, so slowly spin here until systemd kills this
        // nvidia-migmanager process as part of the host shutting down by sending it
        // SIGTERM. This serves as a more obvious line of defense against the
        // boot proceeding past a required reboot.
        loop {
            thread::sleep(Duration::from_secs(5));
            info!("Still waiting for the host to be rebooted...");
        }
    } else {
        info!("GPU reset not required.");
    }

    Ok(())
}

fn run() -> Result<()> {
    let args: Args = argh::from_env();

    // SimpleLogger will send errors to stderr and anything less to stdout.
    let log_level = args.log_level.unwrap_or(LevelFilter::Info);
    SimpleLogger::init(log_level, LogConfig::default()).context(error::LoggerSnafu)?;

    info!("nvidia-migmanager started");

    let mig_settings = get_mig_settings(args.config_path)?;
    let gpu_info = get_gpu_info()?;

    match args.subcommand {
        Subcommand::HandleMigManager(_) => handle_mig_manager(mig_settings, &gpu_info),
        Subcommand::RebootIfRequired(_) => reboot_if_required(),
    }
}

fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        process::exit(1);
    }
}

// =^..^=   =^..^=   =^..^=   =^..^=   =^..^=   =^..^=   =^..^=   =^..^=   =^..^=   =^..^=   =^..^=

mod error {
    use snafu::Snafu;
    use std::path::PathBuf;
    use std::process::{Command, Output};

    #[derive(Debug, Snafu)]
    #[snafu(visibility(pub(super)))]
    pub(super) enum Error {
        #[snafu(display("Failed to read settings from config at {}: {}", config_path.display(), source))]
        ReadConfig {
            config_path: PathBuf,
            source: std::io::Error,
        },

        #[snafu(display("Failed to write marker file at {}. Error: {}", marker_path.display(), source))]
        WriteMarker {
            marker_path: PathBuf,
            source: std::io::Error,
        },

        #[snafu(display("Failed to deserialize settings from config at {}: {}", config_path.display(), source))]
        TomlDeserialization {
            config_path: PathBuf,
            source: toml::de::Error,
        },

        #[snafu(display("Failed to deserialize MIG profile: {}", source))]
        Deserialization { source: serde_plain::Error },

        #[snafu(display("'{}' failed - stderr: {}",
                        bin_path, String::from_utf8_lossy(&output.stderr)))]
        CommandFailure { bin_path: String, output: Output },

        #[snafu(display("Failed to execute '{:?}': {}", command, source))]
        ExecutionFailure {
            command: Box<Command>,
            source: std::io::Error,
        },

        #[snafu(display("Logger setup error: {}", source))]
        Logger { source: log::SetLoggerError },

        #[snafu(display("Nvidia GPU not available."))]
        GpuModel {},

        #[snafu(display("Invalid MIG Profile provided in the Settings."))]
        MigProfile {},

        #[snafu(display("MIG is unsupported because multiple variants of Nvidia GPU present."))]
        MigGpu {},

        #[snafu(display("NvidiaSmi command failed or has incorrect output format."))]
        NvidiaSmi {},
    }
}

type Result<T> = std::result::Result<T, error::Error>;

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_get_mig_settings() {
        let config_toml = r#"
            device-partitioning-strategy = "mig"
            profile = { "a100.40gb" = "1g.5gb" }
        "#;

        let temp_dir = tempfile::TempDir::new().unwrap();
        let temp_config = Path::join(temp_dir.path(), "nvidia-migmanager.toml");
        std::fs::write(&temp_config, config_toml).unwrap();

        let mig_settings = get_mig_settings(&temp_config).unwrap();
        let mut mig_profile = HashMap::new();
        mig_profile.insert("a100.40gb".to_string(), "1g.5gb".to_string());

        let expected_mig_settings = NvidiaMigConfig {
            device_partitioning_strategy: "mig".to_string(),
            profile: mig_profile,
        };

        assert_eq!(mig_settings, expected_mig_settings)
    }

    #[test]
    fn test_get_mig_settings_default_profiles() {
        let config_toml = r#"
            device-partitioning-strategy = "mig"
        "#;

        let temp_dir = tempfile::TempDir::new().unwrap();
        let temp_config = Path::join(temp_dir.path(), "nvidia-migmanager.toml");
        std::fs::write(&temp_config, config_toml).unwrap();

        let mig_settings = get_mig_settings(&temp_config).unwrap();
        let mig_profile = HashMap::new();

        let expected_mig_settings = NvidiaMigConfig {
            device_partitioning_strategy: "mig".to_string(),
            profile: mig_profile,
        };

        assert_eq!(mig_settings, expected_mig_settings)
    }

    #[test]
    fn test_get_mig_profile_deserialization() {
        let mig_profile = "1g.5gb".to_string();
        let profile =
            serde_plain::from_str::<NvidiaA100_40gbMigProfile>(mig_profile.as_str()).unwrap();

        let profile_string = profile.get_mig_profile();
        let expected_profile_string = "1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb";

        assert_eq!(profile_string, expected_profile_string)
    }

    #[test]
    fn test_get_mig_profile_deserialization_default() {
        let mig_profile = "1g.8gb".to_string();
        let profile =
            serde_plain::from_str::<NvidiaA100_40gbMigProfile>(mig_profile.as_str()).unwrap();
        let profile_string = profile.get_mig_profile();
        let expected_profile_string = "7g.40gb";

        assert_eq!(profile_string, expected_profile_string)
    }

    #[test]
    fn test_get_gpu_model_rtx_pro_4500() {
        let gpu = get_gpu_model("0x2C3A10DE").unwrap();
        assert_eq!(gpu, NvidiaGpu::RtxPro4500_32GB)
    }

    #[test]
    fn test_get_mig_profile_rtx_pro_4500() {
        for (input, expected) in [
            ("1g.16gb", "1g.16gb,1g.16gb"),
            ("2", "1g.16gb,1g.16gb"),
            ("2g.32gb", "2g.32gb"),
            ("1", "2g.32gb"),
            ("unknown", "2g.32gb"),
        ] {
            let profile = serde_plain::from_str::<NvidiaRtxPro4500_32gbMigProfile>(input).unwrap();
            assert_eq!(profile.get_mig_profile(), expected);
        }
    }

    #[test]
    fn test_get_mig_profile_unknown_gpu() {
        let gpu = "a100.40gb";
        let mig_profile = "1g.5gb";

        let gpu_regex = Regex::new(GPU_MODEL_REGEX).unwrap();
        let profile_regex = Regex::new(MIG_PROFILE_REGEX).unwrap();

        let gpu_ram: usize = gpu_regex
            .captures(gpu)
            .map(|captures| captures[1].parse().unwrap_or(0))
            .unwrap();
        let (compute_slices, slice_ram) = profile_regex
            .captures(mig_profile)
            .map(|captures| {
                (
                    captures[1].parse().unwrap_or(0),
                    captures[2].parse().unwrap_or(0),
                )
            })
            .unwrap();

        let num_slices: usize = min(gpu_ram / slice_ram, 7 / compute_slices);

        let profile_string = std::iter::repeat_n(mig_profile, num_slices)
            .collect::<Vec<_>>()
            .join(",");

        let expected_profile_string = "1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb";

        assert_eq!(profile_string, expected_profile_string)
    }
}
