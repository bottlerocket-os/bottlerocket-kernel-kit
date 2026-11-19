%global nvlsm_major 2025
%global nvlsm_minor 12
%global nvlsm_patch 211
%global nvlsm_ver %{nvlsm_major}.%{nvlsm_minor}.%{nvlsm_patch}
# Both `lib/libgrpc_mgr.so` and `sbin/nvlsm` have RPATHs set to `opt/nvidia/nvlsm` which causes the RPATH check to fail.
%global __brp_check_rpaths %{nil}
%if "%{?_cross_arch}" == "aarch64"
%global nvidia_arch sbsa
%else
%global nvidia_arch %{_cross_arch}
%endif

Name: %{_cross_os}nvlsm
Version: %{nvlsm_ver}
Release: 1%{?dist}
Summary: NVIDIA Subnet Manager component
License: LicenseRef-NVIDIA-AWS-EULA
URL: https://nvidia.com

# NVIDIA rpms and license files from 0 to 199
Source0: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/nvlsm-%{nvlsm_ver}-1.x86_64.rpm
Source1: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/sbsa/nvlsm-%{nvlsm_ver}-1.aarch64.rpm
Source2: NVidiaEULAforAWS.pdf

# NVLSM configuration files
Source200: nvlsm.service
Source201: nvlsm-online.service
Source202: infiniband-guid.service
Source203: nvlsm-tempfiles.conf
Source204: nvlsm-ld.so.conf.in

%description
%{summary}.

%prep
# Extract Subnet Manager from the rpm via cpio rather than `%%setup` since the
# correct source is architecture-dependent.
mkdir nvlsm-linux-%{nvidia_arch}-%{nvlsm_ver}-archive
rpm2cpio %{_sourcedir}/nvlsm-%{nvlsm_ver}-1.%{_cross_arch}.rpm | cpio -idmV -D nvlsm-linux-%{nvidia_arch}-%{nvlsm_ver}-archive

# Add the license.
install -p -m 0644 %{S:2} .

%install
pushd nvlsm-linux-%{nvidia_arch}-%{nvlsm_ver}-archive

# Install binary
install -d %{buildroot}%{_cross_bindir}
install -p -m 0755 opt/nvidia/nvlsm/sbin/nvlsm %{buildroot}%{_cross_bindir}

# Install shared libraries under nvidia libdir
install -d %{buildroot}%{_cross_libdir}/nvidia/nvlsm
install -p -m 0644 opt/nvidia/nvlsm/lib/*.so %{buildroot}%{_cross_libdir}/nvidia/nvlsm

# Configuration files that are referenced but do not need to be updated at runtime
install -d %{buildroot}%{_cross_datadir}/nvidia/nvlsm
install -p -m 0644 usr/share/nvidia/nvlsm/*.conf %{buildroot}%{_cross_datadir}/nvidia/nvlsm

popd

# Install configuration files
install -d %{buildroot}%{_cross_unitdir}
install -p -m 0644 %{S:200} %{S:201} %{S:202} %{buildroot}%{_cross_unitdir}

install -d %{buildroot}%{_cross_tmpfilesdir}
install -p -m 0644 %{S:203} %{buildroot}%{_cross_tmpfilesdir}/nvlsm.conf

install -d %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/ld.so.conf.d/
# We need to add `_cross_libdir/nvidia/nvlsm` to the paths loaded by the ldconfig service
sed -e 's|__LIBDIR__|%{_cross_libdir}|' %{S:204} > nvlsm.conf
install -m 0644 nvlsm.conf %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/ld.so.conf.d/

%files
%{_cross_attribution_file}
%license NVidiaEULAforAWS.pdf
%license nvlsm-linux-%{nvidia_arch}-%{nvlsm_ver}-archive/usr/share/nvidia/nvlsm/third-party-notices.txt

%{_cross_bindir}/nvlsm

%dir %{_cross_libdir}/nvidia/nvlsm
%{_cross_libdir}/nvidia/nvlsm/libgrpc_mgr.so

%{_cross_tmpfilesdir}/nvlsm.conf

%dir %{_cross_datadir}/nvidia/nvlsm
%{_cross_datadir}/nvidia/nvlsm/device_configuration.conf
%{_cross_datadir}/nvidia/nvlsm/grpc_mgr.conf
%{_cross_datadir}/nvidia/nvlsm/nvlsm.conf

%{_cross_factorydir}%{_cross_sysconfdir}/ld.so.conf.d/nvlsm.conf

%{_cross_unitdir}/nvlsm.service
%{_cross_unitdir}/nvlsm-online.service
%{_cross_unitdir}/infiniband-guid.service
