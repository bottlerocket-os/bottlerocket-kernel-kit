# nvidia-migmanager

Current version: 0.1.0

## NVIDIA MIG Manager
`nvidia-migmanager` ensures that MIG settings are applied to an instance that supports
it. It is called by `nvidia-migmanager.service`.

The binary reads its config file and based on the config, it activates/deactivates MIG
and applies the profile according to the type of GPU present in the instance.

NVIDIA MIG is supported in A30, A100, H100, H200, B200, B300, RTX PRO 6000 and RTX PRO 4500 GPUs.

### Example:
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

## Colophon

This text was generated using [cargo-readme](https://crates.io/crates/cargo-readme), and includes the rustdoc from `src/main.rs`.
