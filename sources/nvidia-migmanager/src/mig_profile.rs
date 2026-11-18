use serde::Deserialize;

pub(crate) trait MigGpuProfile: for<'de> Deserialize<'de> {
    fn get_mig_profile(&self) -> &str;
}

#[derive(Deserialize)]
pub(crate) enum NvidiaA100_40gbMigProfile {
    #[serde(alias = "1g.5gb")]
    #[serde(alias = "7")]
    Mig1g5gb,

    #[serde(alias = "1g.10gb")]
    #[serde(alias = "4")]
    Mig1g10gb,

    #[serde(alias = "2g.10gb")]
    #[serde(alias = "3")]
    Mig2g10gb,

    #[serde(alias = "3g.20gb")]
    #[serde(alias = "2")]
    Mig3g20gb,

    #[serde(alias = "7g.40gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig7g40gb,
}

impl MigGpuProfile for NvidiaA100_40gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            NvidiaA100_40gbMigProfile::Mig7g40gb => "7g.40gb",
            NvidiaA100_40gbMigProfile::Mig3g20gb => "3g.20gb,3g.20gb",
            NvidiaA100_40gbMigProfile::Mig2g10gb => "2g.10gb,2g.10gb,2g.10gb",
            NvidiaA100_40gbMigProfile::Mig1g10gb => "1g.10gb,1g.10gb,1g.10gb,1g.10gb",
            NvidiaA100_40gbMigProfile::Mig1g5gb => {
                "1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb,1g.5gb"
            }
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaA100_80gbMigProfile {
    #[serde(alias = "1g.10gb")]
    #[serde(alias = "7")]
    Mig1g10gb,

    #[serde(alias = "1g.20gb")]
    #[serde(alias = "4")]
    Mig1g20gb,

    #[serde(alias = "2g.20gb")]
    #[serde(alias = "3")]
    Mig2g20gb,

    #[serde(alias = "3g.40gb")]
    #[serde(alias = "2")]
    Mig3g40gb,

    #[serde(alias = "7g.80gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig7g80gb,
}

impl MigGpuProfile for NvidiaA100_80gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            NvidiaA100_80gbMigProfile::Mig7g80gb => "7g.80gb",
            NvidiaA100_80gbMigProfile::Mig3g40gb => "3g.40gb,3g.40gb",
            NvidiaA100_80gbMigProfile::Mig2g20gb => "2g.20gb,2g.20gb,2g.20gb",
            NvidiaA100_80gbMigProfile::Mig1g20gb => "1g.20gb,1g.20gb,1g.20gb,1g.20gb",
            NvidiaA100_80gbMigProfile::Mig1g10gb => {
                "1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb"
            }
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaH100_80gbMigProfile {
    #[serde(alias = "1g.10gb")]
    #[serde(alias = "7")]
    Mig1g10gb,

    #[serde(alias = "1g.20gb")]
    #[serde(alias = "4")]
    Mig1g20gb,

    #[serde(alias = "2g.20gb")]
    #[serde(alias = "3")]
    Mig2g20gb,

    #[serde(alias = "3g.40gb")]
    #[serde(alias = "2")]
    Mig3g40gb,

    #[serde(alias = "7g.80gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig7g80gb,
}

impl MigGpuProfile for NvidiaH100_80gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            NvidiaH100_80gbMigProfile::Mig7g80gb => "7g.80gb",
            NvidiaH100_80gbMigProfile::Mig3g40gb => "3g.40gb,3g.40gb",
            NvidiaH100_80gbMigProfile::Mig2g20gb => "2g.20gb,2g.20gb,2g.20gb",
            NvidiaH100_80gbMigProfile::Mig1g20gb => "1g.20gb,1g.20gb,1g.20gb,1g.20gb",
            NvidiaH100_80gbMigProfile::Mig1g10gb => {
                "1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb"
            }
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaH200_141gbMigProfile {
    #[serde(alias = "1g.18gb")]
    #[serde(alias = "7")]
    Mig1g18gb,

    #[serde(alias = "1g.35gb")]
    #[serde(alias = "4")]
    Mig1g35gb,

    #[serde(alias = "2g.35gb")]
    #[serde(alias = "3")]
    Mig2g35gb,

    #[serde(alias = "3g.71gb")]
    #[serde(alias = "2")]
    Mig3g71gb,

    #[serde(alias = "7g.141gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig7g141gb,
}

impl MigGpuProfile for NvidiaH200_141gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            NvidiaH200_141gbMigProfile::Mig7g141gb => "7g.141gb",
            NvidiaH200_141gbMigProfile::Mig3g71gb => "3g.71gb,3g.71gb",
            NvidiaH200_141gbMigProfile::Mig2g35gb => "2g.35gb,2g.35gb,2g.35gb",
            NvidiaH200_141gbMigProfile::Mig1g35gb => "1g.35gb,1g.35gb,1g.35gb,1g.35gb",
            NvidiaH200_141gbMigProfile::Mig1g18gb => {
                "1g.18gb,1g.18gb,1g.18gb,1g.18gb,1g.18gb,1g.18gb,1g.18gb"
            }
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaB200_180gbMigProfile {
    #[serde(alias = "1g.23gb")]
    #[serde(alias = "7")]
    Mig1g23gb,

    #[serde(alias = "1g.45gb")]
    #[serde(alias = "4")]
    Mig1g45gb,

    #[serde(alias = "2g.45gb")]
    #[serde(alias = "3")]
    Mig2g45gb,

    #[serde(alias = "3g.90gb")]
    #[serde(alias = "2")]
    Mig3g90gb,

    #[serde(alias = "7g.180gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig7g180gb,
}

impl MigGpuProfile for NvidiaB200_180gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            NvidiaB200_180gbMigProfile::Mig7g180gb => "7g.180gb",
            NvidiaB200_180gbMigProfile::Mig3g90gb => "3g.90gb,3g.90gb",
            NvidiaB200_180gbMigProfile::Mig2g45gb => "2g.45gb,2g.45gb,2g.45gb",
            NvidiaB200_180gbMigProfile::Mig1g45gb => "1g.45gb,1g.45gb,1g.45gb,1g.45gb",
            NvidiaB200_180gbMigProfile::Mig1g23gb => {
                "1g.23gb,1g.23gb,1g.23gb,1g.23gb,1g.23gb,1g.23gb,1g.23gb"
            }
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaRtxPro6000_96gbMigProfile {
    #[serde(alias = "1g.24gb")]
    #[serde(alias = "4")]
    Mig1g24gb,

    #[serde(alias = "2g.48gb")]
    #[serde(alias = "2")]
    Mig2g48gb,

    #[serde(alias = "4g.96gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig4g96gb,
}

impl MigGpuProfile for NvidiaRtxPro6000_96gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            NvidiaRtxPro6000_96gbMigProfile::Mig4g96gb => "4g.96gb",
            NvidiaRtxPro6000_96gbMigProfile::Mig2g48gb => "2g.48gb,2g.48gb",
            NvidiaRtxPro6000_96gbMigProfile::Mig1g24gb => "1g.24gb,1g.24gb,1g.24gb,1g.24gb",
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaRtxPro4500_32gbMigProfile {
    #[serde(alias = "1g.16gb")]
    #[serde(alias = "2")]
    Mig1g16gb,

    #[serde(alias = "2g.32gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig2g32gb,
}

impl MigGpuProfile for NvidiaRtxPro4500_32gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            Self::Mig2g32gb => "2g.32gb",
            Self::Mig1g16gb => "1g.16gb,1g.16gb",
        }
    }
}

#[derive(Deserialize)]
pub(crate) enum NvidiaB300_269gbMigProfile {
    #[serde(alias = "1g.34gb")]
    #[serde(alias = "7")]
    Mig1g34gb,

    #[serde(alias = "1g.67gb")]
    #[serde(alias = "4")]
    Mig1g67gb,

    #[serde(alias = "2g.67gb")]
    #[serde(alias = "3")]
    Mig2g67gb,

    #[serde(alias = "3g.135gb")]
    #[serde(alias = "2")]
    Mig3g135gb,

    #[serde(alias = "4g.135gb")]
    Mig4g135gb,

    #[serde(alias = "7g.269gb")]
    #[serde(alias = "1")]
    #[serde(other)]
    Mig7g269gb,
}

impl MigGpuProfile for NvidiaB300_269gbMigProfile {
    fn get_mig_profile(&self) -> &str {
        match self {
            Self::Mig7g269gb => "7g.269gb",
            Self::Mig4g135gb => "4g.135gb",
            Self::Mig3g135gb => "3g.135gb,3g.135gb",
            Self::Mig2g67gb => "2g.67gb,2g.67gb,2g.67gb",
            Self::Mig1g67gb => "1g.67gb,1g.67gb,1g.67gb,1g.67gb",
            Self::Mig1g34gb => "1g.34gb,1g.34gb,1g.34gb,1g.34gb,1g.34gb,1g.34gb,1g.34gb",
        }
    }
}
