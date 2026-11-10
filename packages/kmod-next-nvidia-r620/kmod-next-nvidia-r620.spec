%global driver_major 620
%global driver_minor 70
%global driver_patch 06
%global driver_ver %{driver_major}.%{driver_minor}.%{driver_patch}
%global imex_ver 2.0.0.rel49
%global fm_ver 2.0.0.rel106
%global gdrcopy_ver 2.6
# NVIDIA path macros namespaced to the "lts" branch; overlaid onto canonical paths at boot.
%cross_nvidia_paths lts

%global kernel_major next
%global kernel_sources %{_cross_usrsrc}/kernels/%{kernel_major}

# With the split of the firmware binary from firmware/gsp.bin to firmware/gsp_ga10x.bin
# and firmware/gsp_tu10x.bin the file format changed from executable to relocatable.
# The __spec_install_post macro will by default try to strip all binary files.
# Unfortunately the strip used is not compatible with the new file format.
# Redefine strip, so that these firmware binaries do not derail the build.
%global __strip /usr/bin/true

%global driver_dir NVIDIA-Linux-%{_cross_arch}-%{driver_ver}
%global imex_rpm nvidia-imex-direct-%{imex_ver}-1.%{_cross_arch}.rpm
%global imex_dir nvidia-imex-%{imex_ver}
%global fm_rpm nvidia-fabricmanager-direct-%{fm_ver}-1.%{_cross_arch}.rpm
%global fm_dir nvidia-fabricmanager-%{fm_ver}

%global nscq_rpm libnvidia-nscq-%{driver_ver}-1.amzn2023.%{_cross_arch}.rpm
%global nscq_dir libnvidia-nscq-%{driver_ver}

Name: %{_cross_os}kmod-next-nvidia-r620
Version: %{driver_ver}
Release: 1%{?dist}
Summary: NVIDIA r620 drivers for the next kernel
License: (Apache-2.0 OR MIT) AND Zlib
URL: http://www.nvidia.com/

# NVIDIA archives and license files from 0 to 199
# NVIDIA .run scripts for kernel and userspace drivers
Source0: https://us.download.nvidia.com/tesla/%{driver_ver}/NVIDIA-Linux-x86_64-%{driver_ver}.run
Source1: https://us.download.nvidia.com/tesla/%{driver_ver}/NVIDIA-Linux-aarch64-%{driver_ver}.run
Source3: NVidiaEULAforAWS.pdf
Source4: COPYING

# fabricmanager for NVSwitch
Source10: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/nvidia-fabricmanager-direct-%{fm_ver}-1.x86_64.rpm
Source11: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/sbsa/nvidia-fabricmanager-direct-%{fm_ver}-1.aarch64.rpm

# IMEX for GB200
Source20: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/nvidia-imex-direct-%{imex_ver}-1.x86_64.rpm
Source21: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/sbsa/nvidia-imex-direct-%{imex_ver}-1.aarch64.rpm

# NSCQ (NVSwitch Configuration and Query) library
Source30: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/libnvidia-nscq-%{driver_ver}-1.amzn2023.x86_64.rpm
Source31: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/sbsa/libnvidia-nscq-%{driver_ver}-1.amzn2023.aarch64.rpm

# Common NVIDIA conf files from 200 to 299
Source200: nvidia-tmpfiles.conf.in
Source202: nvidia-dependencies-modules-load.conf
Source203: nvidia-fabricmanager.service
Source204: nvidia-fabricmanager.cfg
Source205: nvidia-sysusers.conf
Source206: nvidia-persistenced.service
Source207: fabricmanager.env
Source208: nvidia-imex.service
Source209: nvidia-imex.cfg
Source210: nvidia-imex-tmpfiles.conf
Source211: nvidia-imex-default-channel.conf

# NVIDIA tesla conf files from 300 to 399
Source300: nvidia-tesla-lts-tmpfiles.conf

# Driverdog config templates from 400 to 499
Source400: nvidia-open-gpu-lts-config.toml.in
Source401: nvidia-open-gpu-copy-only-lts-config.toml.in

# Systemd service templates from 500 to 599
Source500: copy-open-gpu-lts-kernel-modules.service.in
Source501: load-open-gpu-lts-kernel-modules.service.in

Source600: nvidia-gdrcopy-open-gpu-lts-config.toml.in
Source601: copy-gdrcopy-open-gpu-lts-kernel-module.service.in
Source602: load-gdrcopy-open-gpu-lts-kernel-module.service.in
Source603: nvidia-gdrcopy-lts-tmpfiles.conf

# GDRcopy
Source700: https://github.com/NVIDIA/gdrcopy/archive/v%{gdrcopy_ver}/gdrcopy-%{gdrcopy_ver}.tar.gz

# Overlay activation units, split by concern: driver (lib/bin/modules) and config
# (/etc). Run unconditionally in a single-driver image; gated per-branch by
# the nvidia-select-branch gate drop-ins in a dual-branch image.
Source800: nvidia-lts-overlay-driver.service.in
Source801: nvidia-lts-overlay-config.service.in
Source802: nvidia-lts-ldconfig.service

Patch001: 0001-makefile-allow-to-use-any-kernel-arch.patch

BuildRequires: %{_cross_os}kernel-next-devel
Requires: %{_cross_os}kernel-next
Requires: %{_cross_os}nvidia-migmanager
Requires: %{name}-tesla
Requires: %{name}-open-gpu
Requires: %{name}-mps

Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}

%description
%{summary}.

%package imex
Summary: NVIDIA IMEX binaries, config, and service files
License: LicenseRef-NVIDIA-AWS-EULA AND GPL-2.0-only
Requires: %{name}
Requires: %{_cross_os}libstdc++
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-imex

%description imex
%{summary}.

%package imex-config
Summary: NVIDIA IMEX modprobe configuration
Requires: %{name}-imex

%description imex-config
%{summary}.

%package fabricmanager
Summary: NVIDIA fabricmanager config and service files
Requires: %{name}-tesla(fabricmanager)
Requires: %{_cross_os}nvlsm
Requires: %{name}-imex
Requires: %{name}-nscq
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-fabricmanager

%description fabricmanager
%{summary}.

%package nscq
Summary: NVIDIA NSCQ (NVSwitch Configuration and Query) library
License: LicenseRef-NVIDIA-AWS-EULA
Requires: %{name}
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-nscq

%description nscq
%{summary}.

%package open-gpu
Summary: NVIDIA %{driver_major} Open GPU driver
Version: %{driver_ver}
License: MIT AND GPL-2.0-only
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-open-gpu

%description open-gpu
%{summary}.

%package tesla
Summary: NVIDIA %{driver_major} Tesla driver
Version: %{driver_ver}
License: LicenseRef-NVIDIA-AWS-EULA AND GPL-2.0-only
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}
Requires: %{name}-fabricmanager
Requires: %{_cross_os}libstdc++
Provides: %{name}-tesla(fabricmanager)
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-tesla
Provides: %{_cross_os}nvidia-%{nvidia_branch}
# Only one package may provide a given branch alias, and the two branches may
# not co-install unless the nvidia-dual-branch image feature relaxes it
Conflicts: %{_cross_os}nvidia-%{nvidia_branch}
Conflicts: (%{_cross_os}nvidia-pb unless %{_cross_os}image-feature(nvidia-dual-branch))

%description tesla
%{summary}.

%package mps
Summary: NVIDIA CUDA Multi-Process Service
License: LicenseRef-NVIDIA-AWS-EULA AND GPL-2.0-only
Requires: %{name}
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-mps

%description mps
%{summary}.

%package gdrcopy
Summary: NVIDIA GDRCopy driver
Version: %{gdrcopy_ver}
License: MIT AND GPL-2.0-only
Provides: %{_cross_os}kmod-next-nvidia-%{nvidia_branch}-gdrcopy
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}

%description gdrcopy
%{summary}.


%prep
# Extract nvidia sources with `-x`, otherwise the script will try to install
# the driver in the current run
sh %{_sourcedir}/%{driver_dir}.run -x
pushd %{driver_dir}
%patch 1 -p1
popd

# Extract the IMEX, fabric manager, and NSCQ rpms via cpio rather than
# `%%setup`, because the correct source is architecture-dependent.
mkdir %{imex_dir} %{fm_dir} %{nscq_dir}
rpm2cpio %{_sourcedir}/%{imex_rpm} | cpio -idmV -D %{imex_dir}
rpm2cpio %{_sourcedir}/%{fm_rpm} | cpio -idmV -D %{fm_dir}
rpm2cpio %{_sourcedir}/%{nscq_rpm} | cpio -idmV -D %{nscq_dir}

# Add the license.
install -p -m 0644 %{S:3} %{S:4} .
install -p -m 0644 %{imex_dir}/usr/share/licenses/nvidia-imex-direct/LICENSE imex-LICENSE
install -p -m 0644 %{imex_dir}/usr/share/doc/nvidia-imex-direct/third-party-notices.txt imex-third-party-notices.txt
install -p -m 0644 %{fm_dir}/usr/share/licenses/nvidia-fabricmanager-direct/LICENSE fabricmanager-LICENSE
install -p -m 0644 %{fm_dir}/usr/share/doc/nvidia-fabricmanager-direct/third-party-notices.txt fabricmanager-third-party-notices.txt
install -p -m 0644 %{driver_dir}/supported-gpus/LICENSE supported-gpus-LICENSE

%build

# Begin open driver build
pushd %{driver_dir}/kernel-open

# We set IGNORE_CC_MISMATCH even though we are using the same compiler used to
# compile the kernel, if we don't set this flag the compilation fails
make %{?_smp_mflags} ARCH=%{_cross_karch} IGNORE_CC_MISMATCH=1 SYSSRC=%{kernel_sources} CC=%{_cross_target}-gcc LD=%{_cross_target}-ld

# Strip symbols out of the .ko files
for module in *.ko; do
  %{_cross_target}-strip -g --strip-unneeded "${module}"
done

# end open driver build
popd

# Grab the list of supported devices
jq -r '.chips[] | select(.features[] | contains("kernelopen"))' \
  %{driver_dir}/supported-gpus/supported-gpus.json \
  | jq -s '{"open-gpu": .}' > open-gpu-supported-devices.json
# Confirm H100, H200, B200 and B300 (x86_64) and GB200 and GB300 (aarch64) are in
# the resulting file to catch shape changes
%if "%{_cross_arch}" == "x86_64"
open_gpu_required="0x2330 0x2335 0x2901 0x3182"
%else
open_gpu_required="0x2941 0x31C2"
%endif
for devid in ${open_gpu_required}; do
  jq -e --arg devid "${devid}" \
    '."open-gpu"[] | select((."devid" | ascii_upcase) == ($devid | ascii_upcase)) | ."features" | index("kernelopen")' \
    open-gpu-supported-devices.json >/dev/null \
    || { echo "error: GPU ${devid} is not supported by the open driver" >&2; exit 1; }
done

tar -xof %{S:700}
pushd gdrcopy-%{gdrcopy_ver}/src/gdrdrv
NVIDIA_SRC_DIR="%{_builddir}/%{driver_dir}/kernel-open/nvidia" \
NVIDIA_IS_OPENSOURCE=y \
HAVE_VM_FLAGS_SET=y \
HAVE_PROC_OPS=y \
make %{?_smp_mflags} \
  -C %{kernel_sources} \
  M="$PWD" \
  ARCH=%{_cross_karch} \
  CC=%{_cross_target}-gcc \
  LD=%{_cross_target}-ld \
  modules

%{_cross_target}-strip -g --strip-unneeded gdrdrv.ko
mv gdrdrv.ko ../../gdrdrv-open-gpu.ko
popd


%install
install -d %{buildroot}%{nvidia_libdir}
install -d %{buildroot}%{nvidia_libdir}/nvidia/tesla
install -d %{buildroot}%{_cross_tmpfilesdir}
install -d %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{_cross_sysusersdir}
install -d %{buildroot}%{nvidia_bindir}

sed \
  -e "s|__KERNEL_VERSION__|%{kernel_major}|" \
  -e "s|__PREFIX__|%{_cross_prefix}|" %{S:200} > nvidia.conf
install -p -m 0644 nvidia.conf %{buildroot}%{_cross_tmpfilesdir}

# Install modules-load.d drop-in to autoload required kernel modules
install -d %{buildroot}%{_cross_libdir}/modules-load.d
install -p -m 0644 %{S:202} %{buildroot}%{_cross_libdir}/modules-load.d/nvidia-dependencies.conf

# NVIDIA fabric manager service unit and config
install -p -m 0644 %{S:203} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{nvidia_sysconfdir}/nvidia
install -d %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
install -p -m 0644 %{S:204} %{buildroot}%{nvidia_sysconfdir}/nvidia/fabricmanager.cfg
install -p -m 0644 %{S:207} %{buildroot}%{nvidia_sysconfdir}/nvidia/fabricmanager.env

# Begin NVIDIA tesla driver
install -d %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin
install -d %{buildroot}%{_cross_factorydir}/nvidia/%{nvidia_branch}/open-gpu
install -d %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers

install -m 0644 %{S:300} %{buildroot}%{_cross_tmpfilesdir}/nvidia-%{nvidia_branch}-tesla.conf

sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/open-gpu/drivers/|' %{S:400} > \
  nvidia-%{nvidia_branch}-open-gpu.toml
install -m 0644 nvidia-%{nvidia_branch}-open-gpu.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/open-gpu/drivers/|' %{S:401} > \
  nvidia-%{nvidia_branch}-open-gpu-copy-only.toml
install -m 0644 nvidia-%{nvidia_branch}-open-gpu-copy-only.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers

# Services to copy/load modules
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:500} > nvidia-%{nvidia_branch}-copy-open-gpu-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:501} > nvidia-%{nvidia_branch}-load-open-gpu-kernel-modules.service
install -p -m 0644 \
  nvidia-%{nvidia_branch}-copy-open-gpu-kernel-modules.service \
  nvidia-%{nvidia_branch}-load-open-gpu-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}

# open driver
pushd %{driver_dir}/kernel-open
install nvidia.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
install nvidia-uvm.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
install nvidia-modeset.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
install nvidia-peermem.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
install nvidia-drm.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
popd
# end open driver

pushd %{driver_dir}

# add various vulkan icd/config under a branch-namespaced subdir
install -d %{buildroot}%{nvidia_datadir}/vulkan/icd.d
install -d %{buildroot}%{nvidia_datadir}/vulkan/implicit_layer.d
install -m 0644 nvidia_icd.json %{buildroot}%{nvidia_datadir}/vulkan/icd.d/nvidia_icd.json
install -m 0644 nvidia_layers.json %{buildroot}%{nvidia_datadir}/vulkan/icd.d/nvidia_layers.json
install -d %{buildroot}%{nvidia_datadir}/glvnd/egl_vendor.d
install -m 0644 10_nvidia.json %{buildroot}%{nvidia_datadir}/glvnd/egl_vendor.d/10_nvidia.json
install -d %{buildroot}%{nvidia_datadir}/egl/egl_external_platform.d
install -m 0644 09_nvidia_wayland2.json %{buildroot}%{nvidia_datadir}/egl/egl_external_platform.d/09_nvidia_wayland2.json
install -m 0644 15_nvidia_gbm.json %{buildroot}%{nvidia_datadir}/egl/egl_external_platform.d/15_nvidia_gbm.json
ln -rs %{buildroot}%{nvidia_datadir}/vulkan/icd.d/nvidia_layers.json %{buildroot}%{nvidia_datadir}/vulkan/implicit_layer.d/nvidia_layers.json

# Binaries
install -m 755 nvidia-smi %{buildroot}%{nvidia_bindir}
install -m 755 nvidia-debugdump %{buildroot}%{nvidia_bindir}
install -m 755 nvidia-cuda-mps-control %{buildroot}%{nvidia_bindir}
install -m 755 nvidia-cuda-mps-server %{buildroot}%{nvidia_bindir}
install -m 755 nvidia-persistenced %{buildroot}%{nvidia_bindir}
install -m 4755 nvidia-modprobe %{buildroot}%{nvidia_bindir}
install -m 755 nvoptix.bin %{buildroot}%{nvidia_datadir}/nvidia/
ln -rs %{buildroot}%{nvidia_bindir}/nvidia-smi %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-smi
ln -rs %{buildroot}%{nvidia_bindir}/nvidia-debugdump %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-debugdump
ln -rs %{buildroot}%{nvidia_bindir}/nvidia-cuda-mps-control %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-cuda-mps-control
ln -rs %{buildroot}%{nvidia_bindir}/nvidia-cuda-mps-server %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-cuda-mps-server
ln -rs %{buildroot}%{nvidia_bindir}/nvidia-persistenced %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-persistenced

# Users
install -m 0644 %{S:205} %{buildroot}%{_cross_sysusersdir}/nvidia.conf

# Systemd units
install -m 0644 %{S:206} %{buildroot}%{_cross_unitdir}

# We install all the libraries, and filter them out in the 'files' section,
# so we can catch when new libraries are added
install -m 755 *.so* %{buildroot}/%{nvidia_libdir}/

# This library has the same SONAME as libEGL.so.1.1.0, this will cause
# collisions while the symlinks are created. For now, we only symlink
# libEGL.so.1.1.0.
EXCLUDED_LIBS="libEGL.so.%{driver_ver}"

for lib in $(find . -maxdepth 1 -type f -name 'lib*.so.*' -printf '%%P\n'); do
  [[ "${EXCLUDED_LIBS}" =~ "${lib}" ]] && continue
  # Create backwards-compatibility symlink in nvidia/tesla/
  ln -rs "%{buildroot}/%{nvidia_libdir}/${lib}" "%{buildroot}/%{nvidia_libdir}/nvidia/tesla/${lib}"
  soname="$(%{_cross_target}-readelf -d "${lib}" | awk '/SONAME/{print $5}' | tr -d '[]')"
  [ -n "${soname}" ] || continue
  [ "${lib}" == "${soname}" ] && continue
  ln -s "${lib}" %{buildroot}/%{nvidia_libdir}/"${soname}"
done

# 620 splits the boot microcode into ucodes_ga10x.bin and ucodes_tu10x.bin.
# The open GPU modules load them with the gsp files.
# Include the firmware file for GSP support
install -d %{buildroot}%{_cross_libdir}/firmware/nvidia/%{driver_ver}
for fw in gsp_ga10x.bin gsp_tu10x.bin ucodes_ga10x.bin ucodes_tu10x.bin; do
  install -p -m 0644 firmware/${fw} %{buildroot}%{_cross_libdir}/firmware/nvidia/%{driver_ver}
done

popd

# Include the list of devices that have the kernelopen feature. ghostdog reads
# it only on images with the nvidia-dual-branch feature.
install -p -m 0644 open-gpu-supported-devices.json %{buildroot}%{nvidia_datadir}/nvidia/open-gpu-supported-devices.json

# Begin IMEX binaries and configuration files
install -p -m 0755 %{imex_dir}/usr/bin/nvidia-imex %{buildroot}%{nvidia_bindir}
install -p -m 0755 %{imex_dir}/usr/bin/nvidia-imex-ctl %{buildroot}%{nvidia_bindir}

# NVIDIA IMEX service, config, and tmpfiles
install -p -m 0644 %{S:208} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{nvidia_sysconfdir}/nvidia-imex
install -p -m 0644 %{S:209} %{buildroot}%{nvidia_sysconfdir}/nvidia-imex/config.cfg
install -p -m 0644 %{S:210} %{buildroot}%{_cross_tmpfilesdir}/nvidia-imex.conf

# NVIDIA IMEX modprobe config
install -d %{buildroot}%{_cross_libdir}/modprobe.d
install -p -m 0644 %{S:211} %{buildroot}%{_cross_libdir}/modprobe.d/10-nvidia-default-imex-channel.conf

# Begin NVIDIA fabric manager binaries and topologies
pushd %{fm_dir}
install -p -m 0755 usr/bin/nv-fabricmanager %{buildroot}%{nvidia_bindir}
install -p -m 0755 usr/bin/nvswitch-audit %{buildroot}%{nvidia_bindir}
ln -rs %{buildroot}%{nvidia_bindir}/nv-fabricmanager %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nv-fabricmanager
ln -rs %{buildroot}%{nvidia_bindir}/nvswitch-audit %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvswitch-audit

install -d %{buildroot}%{nvidia_datadir}/nvidia/nvswitch
for t in usr/share/nvidia/nvswitch/*_topology ; do
  install -p -m 0644 "${t}" %{buildroot}%{nvidia_datadir}/nvidia/nvswitch
done
popd

# Begin NSCQ library
pushd %{nscq_dir}
install -p -m 0755 usr/lib64/libnvidia-nscq.so.%{driver_ver} %{buildroot}%{nvidia_libdir}

for lib in $(find usr/lib64 -maxdepth 1 -type f -name 'libnvidia-nscq.so.*' -printf '%%P\n'); do
  soname="$(%{_cross_target}-readelf -d "usr/lib64/${lib}" | awk '/SONAME/{print $5}' | tr -d '[]')"
  [ -n "${soname}" ] || continue
  [ "${lib}" == "${soname}" ] && continue
  ln -s "${lib}" %{buildroot}/%{nvidia_libdir}/"${soname}"
done

popd

install -d %{buildroot}%{nvidia_datadir}/nvidia/gdrcopy/open-gpu/drivers

install -p -m 0644 gdrcopy-%{gdrcopy_ver}/gdrdrv-open-gpu.ko \
  %{buildroot}%{nvidia_datadir}/nvidia/gdrcopy/open-gpu/drivers/gdrdrv.ko

install -p -m 0644 gdrcopy-%{gdrcopy_ver}/LICENSE gdrcopy-LICENSE

sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/gdrcopy/open-gpu/drivers/|' %{S:600} > \
  nvidia-%{nvidia_branch}-gdrcopy-open-gpu.toml
install -m 0644 nvidia-%{nvidia_branch}-gdrcopy-open-gpu.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers

sed -e 's|PREFIX|%{_cross_prefix}|g' \
  %{S:601} > nvidia-%{nvidia_branch}-copy-gdrcopy-open-gpu-kernel-module.service
sed -e 's|PREFIX|%{_cross_prefix}|g' \
  %{S:602} > nvidia-%{nvidia_branch}-load-gdrcopy-open-gpu-kernel-module.service
install -p -m 0644 \
  nvidia-%{nvidia_branch}-copy-gdrcopy-open-gpu-kernel-module.service \
  nvidia-%{nvidia_branch}-load-gdrcopy-open-gpu-kernel-module.service \
  %{buildroot}%{_cross_unitdir}

install -p -m 0644 %{S:603} %{buildroot}%{_cross_tmpfilesdir}/nvidia-%{nvidia_branch}-gdrcopy.conf

# Overlay activation services
sed -e 's|__NVIDIA_ROOT__|%{nvidia_root}|g' %{S:800} > nvidia-lts-overlay-driver.service
sed -e 's|__NVIDIA_ROOT__|%{nvidia_root}|g' %{S:801} > nvidia-lts-overlay-config.service
install -p -m 0644 \
  nvidia-lts-overlay-driver.service \
  nvidia-lts-overlay-config.service \
  %{buildroot}%{_cross_unitdir}
install -p -m 0644 %{S:802} %{buildroot}%{_cross_unitdir}/nvidia-lts-ldconfig.service

# Canonical overlay mountpoints. These directories are the targets the overlay
# service mounts onto, and must exist in the image or the mount fails.
install -d %{buildroot}%{_cross_datadir}/nvidia
install -d %{buildroot}%{_cross_datadir}/vulkan
install -d %{buildroot}%{_cross_datadir}/glvnd
install -d %{buildroot}%{_cross_datadir}/egl


%files
%{_cross_attribution_file}
%license supported-gpus-LICENSE
%dir %{_cross_libexecdir}/nvidia
%dir %{_cross_libexecdir}/nvidia/%{nvidia_branch}
%dir %{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla
# Branch-namespaced storage root (overlaid onto canonical paths at boot)
%dir %{_cross_datadir}/.nvidia
%dir %{nvidia_root}
%dir %{nvidia_datadir}
%dir %{nvidia_sysconfdir}
%dir %{nvidia_bindir}
%dir %{nvidia_libdir}
%dir %{nvidia_libdir}/nvidia
%dir %{nvidia_libdir}/nvidia/tesla
%{nvidia_libdir}/nvidia/tesla/*
# Canonical overlay mountpoint
%dir %{_cross_datadir}/nvidia
%dir %{nvidia_datadir}/nvidia
%dir %{_cross_libdir}/modules-load.d
%dir %{_cross_factorydir}%{_cross_sysconfdir}/drivers
# Base package owns the etc/nvidia storage dirs so the overlay service's lowerdirs
# always exist even when the imex subpackage is absent.
%dir %{nvidia_sysconfdir}/nvidia
%dir %{nvidia_sysconfdir}/nvidia-imex
%{_cross_tmpfilesdir}/nvidia.conf
%{_cross_libdir}/modules-load.d/nvidia-dependencies.conf

# Overlay activation services
%{_cross_unitdir}/nvidia-lts-overlay-driver.service
%{_cross_unitdir}/nvidia-lts-overlay-config.service
%{_cross_unitdir}/nvidia-lts-ldconfig.service

%files tesla
%license NVidiaEULAforAWS.pdf
%license fabricmanager-LICENSE fabricmanager-third-party-notices.txt
%dir %{_cross_datadir}/egl
%dir %{nvidia_datadir}/egl
%dir %{nvidia_datadir}/egl/egl_external_platform.d
%dir %{_cross_datadir}/glvnd
%dir %{nvidia_datadir}/glvnd
%dir %{nvidia_datadir}/glvnd/egl_vendor.d
%dir %{_cross_datadir}/vulkan
%dir %{nvidia_datadir}/vulkan
%dir %{nvidia_datadir}/vulkan/icd.d
%dir %{nvidia_datadir}/vulkan/implicit_layer.d
%dir %{_cross_libdir}/firmware/nvidia/%{driver_ver}
%dir %{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin

# Service files for link/copy/loading drivers (branch-namespaced filenames)
%{_cross_unitdir}/nvidia-%{nvidia_branch}-copy-open-gpu-kernel-modules.service
%{_cross_unitdir}/nvidia-%{nvidia_branch}-load-open-gpu-kernel-modules.service

# Binaries
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-debugdump
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-smi
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nv-fabricmanager
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvswitch-audit
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-persistenced
%{nvidia_bindir}/nvidia-debugdump
%{nvidia_bindir}/nvidia-smi
%{nvidia_bindir}/nv-fabricmanager
%{nvidia_bindir}/nvswitch-audit
%{nvidia_bindir}/nvidia-persistenced
%{nvidia_bindir}/nvidia-modprobe

# nvswitch topologies
%dir %{nvidia_datadir}/nvidia/nvswitch
%{nvidia_datadir}/nvidia/nvswitch/dgx2_hgx2_topology
%{nvidia_datadir}/nvidia/nvswitch/dgxa100_hgxa100_topology
%{nvidia_datadir}/nvidia/nvswitch/dgxh100_hgxh100_topology
%{nvidia_datadir}/nvidia/nvswitch/dgxh800_hgxh800_topology
%{nvidia_datadir}/nvidia/nvswitch/mgxh20_nvl16_topology

# Configuration files
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-open-gpu.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-open-gpu-copy-only.toml
%{nvidia_datadir}/nvidia/open-gpu-supported-devices.json

# tmpfiles
%{_cross_tmpfilesdir}/nvidia-%{nvidia_branch}-tesla.conf

# sysuser files
%{_cross_sysusersdir}/nvidia.conf

# systemd units
%{_cross_unitdir}/nvidia-persistenced.service

# ICD / vendor descriptors (branch-namespaced; overlaid onto the canonical path
# by nvidia-lts-overlay-driver.service)
%{nvidia_datadir}/vulkan/icd.d/nvidia_icd.json
%{nvidia_datadir}/vulkan/icd.d/nvidia_layers.json
%{nvidia_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%{nvidia_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%{nvidia_datadir}/egl/egl_external_platform.d/09_nvidia_wayland2.json
%{nvidia_datadir}/egl/egl_external_platform.d/15_nvidia_gbm.json

# We only install the libraries required by all the DRIVER_CAPABILITIES, described here:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html#driver-capabilities

# Utility libs
%{nvidia_libdir}/libnvidia-api.so.1
%{nvidia_libdir}/libnvidia-ml.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-ml.so.1
%{nvidia_libdir}/libnvidia-cfg.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-cfg.so.1
%{nvidia_libdir}/libnvidia-nvvm.so.4
%{nvidia_libdir}/libnvidia-nvvm.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-nvvm70.so.4
%{nvidia_libdir}/libnvidia-fmdrv.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-fmdrv.so.1

# Compute libs
%{nvidia_libdir}/libcuda.so.%{driver_ver}
%{nvidia_libdir}/libcuda.so.1
%{nvidia_libdir}/libcudadebugger.so.%{driver_ver}
%{nvidia_libdir}/libcudadebugger.so.1

%if "%{_cross_arch}" == "aarch64"
%{nvidia_libdir}/libnvcuextend.so.%{driver_ver}
%{nvidia_libdir}/libnvcuextend.so.1
%endif
%{nvidia_libdir}/libnvidia-opencl.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-opencl.so.1
%{nvidia_libdir}/libnvidia-ptxjitcompiler.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-ptxjitcompiler.so.1
%{nvidia_libdir}/libOpenCL.so.1.0.0
%{nvidia_libdir}/libOpenCL.so.1
%{nvidia_libdir}/libnvidia-allocator.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-allocator.so.1
%{nvidia_libdir}/libnvidia-gpucomp.so.%{driver_ver}
%if "%{_cross_arch}" == "x86_64"
%{nvidia_libdir}/libnvidia-pkcs11.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-pkcs11-openssl3.so.%{driver_ver}
%endif
%{nvidia_libdir}/libnvidia-tileiras.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-tileiras.so.1

# Video libs
%{nvidia_libdir}/libvdpau_nvidia.so.%{driver_ver}
%{nvidia_libdir}/libvdpau_nvidia.so.1
%{nvidia_libdir}/libnvidia-encode.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-encode.so.1
%{nvidia_libdir}/libnvidia-opticalflow.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-opticalflow.so.1
%{nvidia_libdir}/libnvcuvid.so.%{driver_ver}
%{nvidia_libdir}/libnvcuvid.so.1

# Graphics libs
%{nvidia_libdir}/libnvidia-eglcore.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-glcore.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-tls.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-glsi.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-rtcore.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-fbc.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-fbc.so.1
%{nvidia_libdir}/libnvoptix.so.%{driver_ver}
%{nvidia_libdir}/libnvoptix.so.1
%if "%{_cross_arch}" == "aarch64"
%{nvidia_libdir}/libnvidia-rmapi-tegra.so.%{driver_ver}
%endif
%{nvidia_datadir}/nvidia/nvoptix.bin

# Graphics GLVND libs
%{nvidia_libdir}/libnvidia-glvkspirv.so.%{driver_ver}
%{nvidia_libdir}/libGLX_nvidia.so.%{driver_ver}
%{nvidia_libdir}/libGLX_nvidia.so.0
%{nvidia_libdir}/libEGL_nvidia.so.%{driver_ver}
%{nvidia_libdir}/libEGL_nvidia.so.0
%{nvidia_libdir}/libGLESv2_nvidia.so.%{driver_ver}
%{nvidia_libdir}/libGLESv2_nvidia.so.2
%{nvidia_libdir}/libGLESv1_CM_nvidia.so.%{driver_ver}
%{nvidia_libdir}/libGLESv1_CM_nvidia.so.1
%{nvidia_libdir}/libnvidia-present.so.%{driver_ver}

# Graphics compat
%{nvidia_libdir}/libEGL.so.1.1.0
%{nvidia_libdir}/libEGL.so.1
%{nvidia_libdir}/libEGL.so.%{driver_ver}
%{nvidia_libdir}/libGL.so.1.7.0
%{nvidia_libdir}/libGL.so.1
%{nvidia_libdir}/libGLESv1_CM.so.1.2.0
%{nvidia_libdir}/libGLESv1_CM.so.1
%{nvidia_libdir}/libGLESv2.so.2.1.0
%{nvidia_libdir}/libGLESv2.so.2

# NGX
%{nvidia_libdir}/libnvidia-ngx.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-ngx.so.1
%{nvidia_libdir}/libnvidia-ngx-builtin-dlssd.so.310.9.0

# Firmware
%{_cross_libdir}/firmware/nvidia/%{driver_ver}/gsp_ga10x.bin
%{_cross_libdir}/firmware/nvidia/%{driver_ver}/gsp_tu10x.bin
%{_cross_libdir}/firmware/nvidia/%{driver_ver}/ucodes_ga10x.bin
%{_cross_libdir}/firmware/nvidia/%{driver_ver}/ucodes_tu10x.bin

# None of these libraries are required by libnvidia-container, so they
# won't be used by a containerized workload
%exclude %{nvidia_libdir}/libGLX.so.0
%exclude %{nvidia_libdir}/libGLdispatch.so.0
%exclude %{nvidia_libdir}/libOpenGL.so.0
%exclude %{nvidia_libdir}/libglxserver_nvidia.so.%{driver_ver}
%exclude %{nvidia_libdir}/libnvidia-gtk2.so.%{driver_ver}
%exclude %{nvidia_libdir}/libnvidia-gtk3.so.%{driver_ver}
%exclude %{nvidia_libdir}/nvidia_drv.so
%exclude %{nvidia_libdir}/libnvidia-egl-gbm.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-gbm.so.1.1.3
%exclude %{nvidia_libdir}/libnvidia-egl-wayland.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-wayland.so.1.1.20
%exclude %{nvidia_libdir}/libnvidia-egl-wayland2.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-wayland2.so.1.0.2
%exclude %{nvidia_libdir}/libnvidia-egl-xcb.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-xcb.so.1.0.6
%exclude %{nvidia_libdir}/libnvidia-egl-xlib.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-xlib.so.1.0.6
%exclude %{nvidia_libdir}/libnvidia-sandboxutils.so.1
%exclude %{nvidia_libdir}/libnvidia-sandboxutils.so.%{driver_ver}
%exclude %{nvidia_libdir}/libnvidia-vksc-core.so.1
%exclude %{nvidia_libdir}/libnvidia-vksc-core.so.%{driver_ver}
%if "%{_cross_arch}" == "x86_64"
%exclude %{nvidia_libdir}/libnvidia-wayland-client.so.%{driver_ver}
%endif

%files open-gpu
%license COPYING
%dir %{nvidia_datadir}/nvidia/open-gpu
%dir %{nvidia_datadir}/nvidia/open-gpu/drivers
%dir %{_cross_factorydir}/nvidia
%dir %{_cross_factorydir}/nvidia/%{nvidia_branch}
%dir %{_cross_factorydir}/nvidia/%{nvidia_branch}/open-gpu

%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-uvm.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-modeset.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-drm.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-peermem.ko

%files imex
%license NVidiaEULAforAWS.pdf
%license imex-LICENSE imex-third-party-notices.txt
%{nvidia_bindir}/nvidia-imex
%{nvidia_bindir}/nvidia-imex-ctl
%{nvidia_libdir}/libnvidia-imex.so.%{driver_ver}
%{nvidia_libdir}/libnvidia-imex.so.1
%{_cross_unitdir}/nvidia-imex.service
%{nvidia_sysconfdir}/nvidia-imex/config.cfg
%{_cross_tmpfilesdir}/nvidia-imex.conf

%files imex-config
%{_cross_libdir}/modprobe.d/10-nvidia-default-imex-channel.conf

%files fabricmanager
%{nvidia_sysconfdir}/nvidia/fabricmanager.cfg
%{nvidia_sysconfdir}/nvidia/fabricmanager.env
%{_cross_unitdir}/nvidia-fabricmanager.service

%files nscq
%license NVidiaEULAforAWS.pdf
%license %{nscq_dir}/usr/share/licenses/libnvidia-nscq/LICENSE
%{nvidia_libdir}/libnvidia-nscq.so.*

%files mps
%license NVidiaEULAforAWS.pdf
%{nvidia_bindir}/nvidia-cuda-mps-control
%{nvidia_bindir}/nvidia-cuda-mps-server
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-cuda-mps-control
%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-cuda-mps-server

%files gdrcopy
%license gdrcopy-LICENSE
%dir %{nvidia_datadir}/nvidia/gdrcopy
%dir %{nvidia_datadir}/nvidia/gdrcopy/open-gpu
%dir %{nvidia_datadir}/nvidia/gdrcopy/open-gpu/drivers
%{nvidia_datadir}/nvidia/gdrcopy/open-gpu/drivers/gdrdrv.ko
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-gdrcopy-open-gpu.toml
%{_cross_tmpfilesdir}/nvidia-%{nvidia_branch}-gdrcopy.conf
%{_cross_unitdir}/nvidia-%{nvidia_branch}-copy-gdrcopy-open-gpu-kernel-module.service
%{_cross_unitdir}/nvidia-%{nvidia_branch}-load-gdrcopy-open-gpu-kernel-module.service
