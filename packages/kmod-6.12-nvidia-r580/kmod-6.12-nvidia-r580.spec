%global tesla_major 580
%global tesla_minor 178
%global tesla_patch 04
%global tesla_ver %{tesla_major}.%{tesla_minor}.%{tesla_patch}
%global grid_ver grid-19.6
%global gdrcopy_ver 2.6
# Branch name for namespaced per-branch paths
%global nvidia_branch lts
# Branch-namespaced storage root for files that are overlaid onto canonical paths
# at boot. Resolved to /usr/share/.nvidia/lts
%global nvidia_root %{_cross_datadir}/.nvidia/%{nvidia_branch}
%global nvidia_datadir     %{nvidia_root}/share
%global nvidia_libdir      %{nvidia_root}/lib64
%global nvidia_bindir      %{nvidia_root}/bin
%global nvidia_sysconfdir %{nvidia_root}/etc
%if "%{?_cross_arch}" == "aarch64"
%global nvidia_arch sbsa
%else
%global nvidia_arch %{_cross_arch}
%endif

%global kernel_major 6.12
%global kernel_sources %{_cross_usrsrc}/kernels/%{kernel_major}

# With the split of the firmware binary from firmware/gsp.bin to firmware/gsp_ga10x.bin
# and firmware/gsp_tu10x.bin the file format changed from executable to relocatable.
# The __spec_install_post macro will by default try to strip all binary files.
# Unfortunately the strip used is not compatible with the new file format.
# Redefine strip, so that these firmware binaries do not derail the build.
%global __strip /usr/bin/true

Name: %{_cross_os}kmod-6.12-nvidia-r580
Version: %{tesla_ver}
Release: 1%{?dist}
Epoch: 1
Summary: NVIDIA r580 drivers for the 6.12 kernel
# We use these licences because we only ship our own software in the main package,
# each subpackage includes the LICENSE file provided by the Licenses.toml file
License: Apache-2.0 OR MIT
URL: http://www.nvidia.com/

# NVIDIA archives and license files from 0 to 199
# NVIDIA .run scripts for kernel and userspace drivers
Source0: https://us.download.nvidia.com/tesla/%{tesla_ver}/NVIDIA-Linux-x86_64-%{tesla_ver}.run
Source1: https://us.download.nvidia.com/tesla/%{tesla_ver}/NVIDIA-Linux-aarch64-%{tesla_ver}.run
Source2: https://s3.amazonaws.com/ec2-linux-nvidia-drivers/%{grid_ver}/NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws.run
Source3: NVidiaEULAforAWS.pdf
Source4: COPYING
Source5: NvidiaGridAWSUserLicenseAgreement.DOCX

# fabricmanager for NVSwitch
Source10: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/nvidia-fabricmanager-%{tesla_ver}-1.amzn2023.x86_64.rpm
Source11: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/sbsa/nvidia-fabricmanager-%{tesla_ver}-1.amzn2023.aarch64.rpm

# IMEX for GB200
Source20: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/nvidia-imex-%{tesla_ver}-1.amzn2023.x86_64.rpm
Source21: https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/sbsa/nvidia-imex-%{tesla_ver}-1.amzn2023.aarch64.rpm

# Common NVIDIA conf files from 200 to 299
Source200: nvidia-tmpfiles.conf.in
Source202: nvidia-dependencies-modules-load.conf
Source203: nvidia-fabricmanager.service
Source204: nvidia-fabricmanager.cfg
Source205: nvidia-sysusers.conf
Source206: nvidia-persistenced.service
Source207: fabricmanager.env
Source208: gridd.conf
Source209: nvidia-gridd.service
Source210: grid-license-check.service
Source211: grid-license-check.timer
Source212: open-gpu-license-fallback.service
Source213: tesla-license-fallback.service
Source214: grid-license-file-check.conf
Source215: nvidia-imex.service
Source216: nvidia-imex.cfg
Source217: nvidia-imex-tmpfiles.conf
Source218: nvidia-imex-default-channel.conf

# NVIDIA tesla conf files from 300 to 399
Source300: nvidia-tesla-lts-tmpfiles.conf
Source301: nvidia-tesla-lts-build-config.toml.in

# Driverdog config templates from 400 to 499
Source400: nvidia-open-gpu-lts-config.toml.in
Source401: nvidia-open-gpu-copy-only-lts-config.toml.in
Source402: nvidia-grid-lts-config.toml.in
Source403: nvidia-grid-copy-only-lts-config.toml.in

# Systemd service templates from 500 to 599
Source500: link-tesla-lts-kernel-modules.service.in
Source501: load-tesla-lts-kernel-modules.service.in
Source502: copy-open-gpu-lts-kernel-modules.service.in
Source503: load-open-gpu-lts-kernel-modules.service.in
Source504: copy-grid-lts-kernel-modules.service.in
Source505: load-grid-lts-kernel-modules.service.in

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

Patch001: 0001-makefile-allow-to-use-any-kernel-arch.patch

BuildRequires: %{_cross_os}kernel-6.12-devel
Requires: %{_cross_os}kernel-6.12
Requires: %{_cross_os}nvidia-migmanager
Requires: %{name}-tesla
Requires: %{name}-open-gpu
%if "%{_cross_arch}" == "x86_64"
Requires: %{name}-grid
%endif
Requires: %{name}-mps

Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}

%description
%{summary}.

%package fabricmanager
Summary: NVIDIA fabricmanager config and service files
Requires: %{name}-tesla(fabricmanager)
Requires: %{_cross_os}nvlsm
Requires: %{name}-imex
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-fabricmanager

%description fabricmanager
%{summary}.

%package imex
Summary: NVIDIA IMEX config and service files
Requires: %{name}
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-imex

%description imex
%{summary}.

%package imex-config
Summary: NVIDIA IMEX modprobe configuration
Requires: %{name}-imex

%description imex-config
%{summary}.

%package open-gpu
Summary: NVIDIA %{tesla_major} Open GPU driver
Version: %{tesla_ver}
License: MIT AND GPL-2.0-only
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-open-gpu

%description open-gpu
%{summary}.

%if "%{_cross_arch}" == "x86_64"
%package grid
Summary: NVIDIA %{tesla_major} GRID driver
Version: %{tesla_ver}
License: MIT AND GPL-2.0-only AND LicenceRef-NVIDIA-GRID-AWS-EULA
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}
Requires: %{_cross_os}libstdc++
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-grid

%description grid
%{summary}.
%endif

%package tesla
Summary: NVIDIA %{tesla_major} Tesla driver
Version: %{tesla_ver}
License: LicenseRef-NVIDIA-AWS-EULA AND GPL-2.0-only
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}
Requires: %{name}-fabricmanager
Provides: %{name}-tesla(fabricmanager)
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-tesla
Provides: %{_cross_os}nvidia-%{nvidia_branch}
# Only one package may provide a given branch alias, and the two branches may
# not co-install unless the nvidia-dual-branch image feature relaxes it
Conflicts: %{_cross_os}nvidia-%{nvidia_branch}
Conflicts: (%{_cross_os}nvidia-pb unless %{_cross_os}image-feature(nvidia-dual-branch))

%description tesla
%{summary}

%package mps
Summary: NVIDIA CUDA Multi-Process Service
Requires: %{name}
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-mps

%description mps
%{summary}.

%package gdrcopy
Summary: NVIDIA GDRCopy driver
Version: %{gdrcopy_ver}
License: MIT AND GPL-2.0-only
Provides: %{_cross_os}kmod-6.12-nvidia-%{nvidia_branch}-gdrcopy
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}

%description gdrcopy
%{summary}.

%prep
# Extract nvidia sources with `-x`, otherwise the script will try to install
# the driver in the current run
sh %{_sourcedir}/NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}.run -x
# Move to the sources directory and apply patch
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}
%patch 1 -p1
popd

# Extract GRID drivers just like Tesla
%if "%{_cross_arch}" == "x86_64"
sh %{_sourcedir}/NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws.run -x
pushd NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws
%patch 1 -p1
popd
%endif

# Extract fabricmanager from the rpm via cpio rather than `%%setup` since the
# correct source is architecture-dependent.
mkdir fabricmanager-linux-%{nvidia_arch}-%{tesla_ver}-archive
rpm2cpio %{_sourcedir}/nvidia-fabricmanager-%{tesla_ver}-1.amzn2023.%{_cross_arch}.rpm | cpio -idmV -D fabricmanager-linux-%{nvidia_arch}-%{tesla_ver}-archive

# Add the license.
install -p -m 0644 %{S:3} %{S:4} %{S:5} .

# Extract imex from the rpm via cpio rather than `%%setup` since the
# correct source is architecture-dependent.
mkdir imex-%{nvidia_arch}-%{tesla_ver}-archive
rpm2cpio %{_sourcedir}/nvidia-imex-%{tesla_ver}-1.amzn2023.%{_cross_arch}.rpm | cpio -idmV -D imex-%{nvidia_arch}-%{tesla_ver}-archive

# This recipe was based in the NVIDIA yum/dnf specs:
# https://github.com/NVIDIA/yum-packaging-precompiled-kmod

%build

# Begin open driver build
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}/kernel-open

# We set IGNORE_CC_MISMATCH even though we are using the same compiler used to
# compile the kernel, if we don't set this flag the compilation fails
make %{?_smp_mflags} ARCH=%{_cross_karch} IGNORE_CC_MISMATCH=1 SYSSRC=%{kernel_sources} CC=%{_cross_target}-gcc LD=%{_cross_target}-ld

# Strip symbols out of the .ko files
for module in *.ko; do
  %{_cross_target}-strip -g --strip-unneeded "${module}"
done

# end open driver build
popd

# Begin proprietary driver build
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}/kernel

# We set IGNORE_CC_MISMATCH even though we are using the same compiler used to
# compile the kernel, if we don't set this flag the compilation fails
make %{?_smp_mflags} ARCH=%{_cross_karch} IGNORE_CC_MISMATCH=1 SYSSRC=%{kernel_sources} CC=%{_cross_target}-gcc LD=%{_cross_target}-ld

%{_cross_target}-strip -g --strip-unneeded nvidia/nv-interface.o
%{_cross_target}-strip -g --strip-unneeded nvidia-uvm.o
%{_cross_target}-strip -g --strip-unneeded nvidia-drm.o
%{_cross_target}-strip -g --strip-unneeded nvidia-peermem/nvidia-peermem.o
%{_cross_target}-strip -g --strip-unneeded nvidia-modeset/nv-modeset-interface.o

# We delete these files since we just stripped the input .o files above, and
# will be build at runtime in the host
rm nvidia{,-modeset,-peermem}.o

# Delete the .ko files created in make command, just to be safe that we
# don't include any linked module in the base image
rm nvidia{,-modeset,-peermem,-drm}.ko

# End proprietary driver build
popd

%if "%{_cross_arch}" == "x86_64"
# Begin GRID build
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}-grid-aws/kernel-open

# We set IGNORE_CC_MISMATCH even though we are using the same compiler used to
# compile the kernel, if we don't set this flag the compilation fails
make %{?_smp_mflags} ARCH=%{_cross_karch} IGNORE_CC_MISMATCH=1 SYSSRC=%{kernel_sources} CC=%{_cross_target}-gcc LD=%{_cross_target}-ld

# Strip symbols out of the .ko files
for module in *.ko; do
  %{_cross_target}-strip -g --strip-unneeded "${module}"
done

# End GRID build
popd
%endif

# Grab the list of supported devices
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}/supported-gpus
# We want to grab all the `kernelopen` enabled chips except for this list that
# is best held back to the proprietary driver
# 10de:1db1 is V100-16G (P3dn)
# 10de:1db5 is V100-32G (P3dn)
# 10de:1eb8 is T4 (G4dn)
# 10de:1eb4 is T4G (G5g)
# 10de:2237 is A10G (G5)
jq -r '.chips[] | select(.features[] | contains("kernelopen")) |
select(.devid != "0x1DB1"
and .devid != "0x1DB5"
and .devid != "0x1EB8"
and .devid != "0x1EB4"
and .devid != "0x2237")' supported-gpus.json | jq -s '{"open-gpu": .}' > open-gpu-supported-devices.json
# confirm "NVIDIA H100" is in the resulting file to catch shape changes
jq -e '."open-gpu"[] | select(."devid" == "0x2330") | ."features"| index("kernelopen")' open-gpu-supported-devices.json
popd

tar -xof %{S:700}
pushd gdrcopy-%{gdrcopy_ver}/src/gdrdrv
NVIDIA_SRC_DIR="%{_builddir}/NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}/kernel-open/nvidia" \
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
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}
# Proprietary driver
install -d %{buildroot}%{nvidia_bindir}
install -d %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin
install -d %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install -d %{buildroot}%{_cross_factorydir}/nvidia/%{nvidia_branch}/tesla
install -d %{buildroot}%{_cross_factorydir}/nvidia/%{nvidia_branch}/open-gpu
%if "%{_cross_arch}" == "x86_64"
install -d %{buildroot}%{_cross_factorydir}/nvidia/%{nvidia_branch}/grid
%endif
install -d %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers

install -m 0644 %{S:300} %{buildroot}%{_cross_tmpfilesdir}/nvidia-%{nvidia_branch}-tesla.conf

sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/tesla/module-objects.d/|' %{S:301} > \
  nvidia-%{nvidia_branch}-tesla.toml
install -m 0644 nvidia-%{nvidia_branch}-tesla.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/open-gpu/drivers/|' %{S:400} > \
  nvidia-%{nvidia_branch}-open-gpu.toml
install -m 0644 nvidia-%{nvidia_branch}-open-gpu.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/open-gpu/drivers/|' %{S:401} > \
  nvidia-%{nvidia_branch}-open-gpu-copy-only.toml
install -m 0644 nvidia-%{nvidia_branch}-open-gpu-copy-only.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers

%if "%{_cross_arch}" == "x86_64"
sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/grid/drivers/|' %{S:402} > \
  nvidia-%{nvidia_branch}-grid.toml
install -m 0644 nvidia-%{nvidia_branch}-grid.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{nvidia_datadir}/nvidia/grid/drivers/|' %{S:403} > \
  nvidia-%{nvidia_branch}-grid-copy-only.toml
install -m 0644 nvidia-%{nvidia_branch}-grid-copy-only.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
%endif

# Services to link/copy/load modules
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:500} > nvidia-%{nvidia_branch}-link-tesla-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:501} > nvidia-%{nvidia_branch}-load-tesla-kernel-modules.service
install -p -m 0644 \
  nvidia-%{nvidia_branch}-link-tesla-kernel-modules.service \
  nvidia-%{nvidia_branch}-load-tesla-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}

sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:502} > nvidia-%{nvidia_branch}-copy-open-gpu-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:503} > nvidia-%{nvidia_branch}-load-open-gpu-kernel-modules.service
install -p -m 0644 \
  nvidia-%{nvidia_branch}-copy-open-gpu-kernel-modules.service \
  nvidia-%{nvidia_branch}-load-open-gpu-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}

%if "%{_cross_arch}" == "x86_64"
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:504} > nvidia-%{nvidia_branch}-copy-grid-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:505} > nvidia-%{nvidia_branch}-load-grid-kernel-modules.service
install -p -m 0644 \
  nvidia-%{nvidia_branch}-copy-grid-kernel-modules.service \
  nvidia-%{nvidia_branch}-load-grid-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}
%endif

# proprietary driver
install kernel/nvidia.mod.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia/nv-interface.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia/nv-kernel.o_binary %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d/nv-kernel.o

# module-common object
install kernel/.module-common.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d/.module-common.o

# uvm
install kernel/nvidia-uvm.mod.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-uvm.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d

# modeset
install kernel/nvidia-modeset.mod.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-modeset/nv-modeset-interface.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-modeset/nv-modeset-kernel.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d

# peermem
install kernel/nvidia-peermem.mod.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-peermem/nvidia-peermem.o %{buildroot}%{nvidia_datadir}/nvidia/tesla/module-objects.d

# drm
install kernel/nvidia-drm.mod.o %{buildroot}/%{nvidia_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-drm.o %{buildroot}/%{nvidia_datadir}/nvidia/tesla/module-objects.d

# open driver
install -d %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
install kernel-open/nvidia.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/

# add various vulkan icd/config under a branch-namespaced subdir
install -d %{buildroot}%{nvidia_datadir}/vulkan/icd.d
install -d %{buildroot}%{nvidia_datadir}/vulkan/implicit_layer.d
install -m 0644 nvidia_icd.json %{buildroot}%{nvidia_datadir}/vulkan/icd.d/nvidia_icd.json
install -m 0644 nvidia_layers.json %{buildroot}%{nvidia_datadir}/vulkan/icd.d/nvidia_layers.json
install -d %{buildroot}%{nvidia_datadir}/glvnd/egl_vendor.d
install -m 0644 10_nvidia.json %{buildroot}%{nvidia_datadir}/glvnd/egl_vendor.d/10_nvidia.json
install -d %{buildroot}%{nvidia_datadir}/egl/egl_external_platform.d
install -m 0644 10_nvidia_wayland.json %{buildroot}%{nvidia_datadir}/egl/egl_external_platform.d/10_nvidia_wayland.json
install -m 0644 15_nvidia_gbm.json %{buildroot}%{nvidia_datadir}/egl/egl_external_platform.d/15_nvidia_gbm.json
ln -rs %{buildroot}%{nvidia_datadir}/vulkan/icd.d/nvidia_layers.json %{buildroot}%{nvidia_datadir}/vulkan/implicit_layer.d/nvidia_layers.json

# uvm
install kernel-open/nvidia-uvm.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/

# modeset
install kernel-open/nvidia-modeset.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/

# peermem
install kernel-open/nvidia-peermem.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/

# drm
install kernel-open/nvidia-drm.ko %{buildroot}%{nvidia_datadir}/nvidia/open-gpu/drivers/
# end open driver

%if "%{_cross_arch}" == "x86_64"
# GRID driver
pushd ../NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws
install -d %{buildroot}%{nvidia_datadir}/nvidia/grid/drivers/
install kernel-open/nvidia.ko %{buildroot}%{nvidia_datadir}/nvidia/grid/drivers/

# uvm
install kernel-open/nvidia-uvm.ko %{buildroot}%{nvidia_datadir}/nvidia/grid/drivers/

# modeset
install kernel-open/nvidia-modeset.ko %{buildroot}%{nvidia_datadir}/nvidia/grid/drivers/

# peermem
install kernel-open/nvidia-peermem.ko %{buildroot}%{nvidia_datadir}/nvidia/grid/drivers/

# drm
install kernel-open/nvidia-drm.ko %{buildroot}%{nvidia_datadir}/nvidia/grid/drivers/

# Install nvidia-gridd and related files
install -m 755 nvidia-gridd %{buildroot}%{nvidia_bindir}/nvidia-gridd
install -m 644 %{S:208} %{buildroot}%{nvidia_sysconfdir}/nvidia/gridd.conf
install -p -m 0644 %{S:209} %{S:210} %{S:211} %{S:212} %{S:213} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{_cross_unitdir}/nvidia-k8s-device-plugin.service.d
install -p -m 0644 %{S:214} %{buildroot}%{_cross_unitdir}/nvidia-k8s-device-plugin.service.d
popd
# End GRID driver
%endif

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
%if "%{_cross_arch}" == "x86_64"
install -m 755 nvidia-ngx-updater %{buildroot}%{nvidia_bindir}
ln -rs %{buildroot}%{nvidia_bindir}/nvidia-ngx-updater %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-ngx-updater
%endif

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
EXCLUDED_LIBS="libEGL.so.%{tesla_ver}"

for lib in $(find . -maxdepth 1 -type f -name 'lib*.so.*' -printf '%%P\n'); do
  [[ "${EXCLUDED_LIBS}" =~ "${lib}" ]] && continue
  # Create backwards-compatibility symlink in nvidia/tesla/
  ln -rs "%{buildroot}/%{nvidia_libdir}/${lib}" "%{buildroot}/%{nvidia_libdir}/nvidia/tesla/${lib}"
  soname="$(%{_cross_target}-readelf -d "${lib}" | awk '/SONAME/{print $5}' | tr -d '[]')"
  [ -n "${soname}" ] || continue
  [ "${lib}" == "${soname}" ] && continue
  ln -s "${lib}" %{buildroot}/%{nvidia_libdir}/"${soname}"
done

# Include the firmware file for GSP support
install -d %{buildroot}%{_cross_libdir}/firmware/nvidia/%{tesla_ver}
install -p -m 0644 firmware/gsp_ga10x.bin %{buildroot}%{_cross_libdir}/firmware/nvidia/%{tesla_ver}
install -p -m 0644 firmware/gsp_tu10x.bin %{buildroot}%{_cross_libdir}/firmware/nvidia/%{tesla_ver}

# Include the open driver supported devices file for runtime matching of the
# driver. This is consumed by ghostdog to match the driver to this list
install -p -m 0644 supported-gpus/open-gpu-supported-devices.json %{buildroot}%{nvidia_datadir}/nvidia/open-gpu-supported-devices.json

popd

# Begin NVIDIA fabric manager binaries and topologies
pushd fabricmanager-linux-%{nvidia_arch}-%{tesla_ver}-archive
install -p -m 0755 usr/bin/nv-fabricmanager %{buildroot}%{nvidia_bindir}
install -p -m 0755 usr/bin/nvswitch-audit %{buildroot}%{nvidia_bindir}
ln -rs %{buildroot}%{nvidia_bindir}/nv-fabricmanager %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nv-fabricmanager
ln -rs %{buildroot}%{nvidia_bindir}/nvswitch-audit %{buildroot}%{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvswitch-audit

install -d %{buildroot}%{nvidia_datadir}/nvidia/tesla/nvswitch
for t in usr/share/nvidia/nvswitch/*_topology ; do
  install -p -m 0644 "${t}" %{buildroot}%{nvidia_datadir}/nvidia/tesla/nvswitch
done

popd

# Begin IMEX binaries and configuration files
pushd imex-%{nvidia_arch}-%{tesla_ver}-archive
install -p -m 0755 usr/bin/nvidia-imex %{buildroot}%{nvidia_bindir}
install -p -m 0755 usr/bin/nvidia-imex-ctl %{buildroot}%{nvidia_bindir}

popd

# NVIDIA IMEX service, config, and tmpfiles
install -p -m 0644 %{S:215} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{nvidia_sysconfdir}/nvidia-imex
install -p -m 0644 %{S:216} %{buildroot}%{nvidia_sysconfdir}/nvidia-imex/config.cfg
install -p -m 0644 %{S:217} %{buildroot}%{_cross_tmpfilesdir}/nvidia-imex.conf

# NVIDIA IMEX modprobe config
install -d %{buildroot}%{_cross_libdir}/modprobe.d
install -p -m 0644 %{S:218} %{buildroot}%{_cross_libdir}/modprobe.d/10-nvidia-default-imex-channel.conf

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

# Canonical overlay mountpoints. These directories are the targets the overlay
# service mounts onto, and must exist in the image or the mount fails.
install -d %{buildroot}%{_cross_datadir}/nvidia
install -d %{buildroot}%{_cross_datadir}/vulkan
install -d %{buildroot}%{_cross_datadir}/glvnd
install -d %{buildroot}%{_cross_datadir}/egl

%files
%{_cross_attribution_file}
%dir %{_cross_libexecdir}/nvidia
# Branch-namespaced storage root (overlaid onto canonical paths at boot)
%dir %{_cross_datadir}/.nvidia
%dir %{nvidia_root}
%dir %{nvidia_datadir}
%dir %{nvidia_sysconfdir}
%dir %{nvidia_libdir}
%dir %{nvidia_libdir}/nvidia/tesla
%{nvidia_libdir}/nvidia/tesla/*
# Canonical overlay mountpoint
%dir %{_cross_datadir}/nvidia
%dir %{_cross_libdir}/modules-load.d
%dir %{_cross_factorydir}%{_cross_sysconfdir}/drivers
# Base package owns the etc/nvidia storage dirs so the overlay service's lowerdirs
# always exist even when the fabricmanager/grid/imex subpackages are absent.
%dir %{nvidia_sysconfdir}/nvidia
%dir %{nvidia_sysconfdir}/nvidia-imex
%{_cross_tmpfilesdir}/nvidia.conf
%{_cross_libdir}/modules-load.d/nvidia-dependencies.conf

# Overlay activation services
%{_cross_unitdir}/nvidia-lts-overlay-driver.service
%{_cross_unitdir}/nvidia-lts-overlay-config.service

%files tesla
%license NVidiaEULAforAWS.pdf
%license fabricmanager-linux-%{nvidia_arch}-%{tesla_ver}-archive/usr/share/licenses/nvidia-fabricmanager/third-party-notices.txt
%dir %{_cross_datadir}/egl
%dir %{nvidia_datadir}/egl
%dir %{nvidia_datadir}/egl/egl_external_platform.d
%dir %{_cross_datadir}/glvnd
%dir %{nvidia_datadir}/glvnd
%dir %{nvidia_datadir}/glvnd/egl_vendor.d
%dir %{nvidia_datadir}/nvidia/tesla
%dir %{nvidia_datadir}/nvidia/tesla/module-objects.d
%dir %{_cross_datadir}/vulkan
%dir %{nvidia_datadir}/vulkan
%dir %{nvidia_datadir}/vulkan/icd.d
%dir %{nvidia_datadir}/vulkan/implicit_layer.d
%dir %{_cross_factorydir}/nvidia/%{nvidia_branch}/tesla
%dir %{_cross_libdir}/firmware/nvidia/%{tesla_ver}
%dir %{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin

# Service files for link/copy/loading drivers (branch-namespaced filenames)
%{_cross_unitdir}/nvidia-%{nvidia_branch}-link-tesla-kernel-modules.service
%{_cross_unitdir}/nvidia-%{nvidia_branch}-load-tesla-kernel-modules.service
%{_cross_unitdir}/nvidia-%{nvidia_branch}-copy-open-gpu-kernel-modules.service
%{_cross_unitdir}/nvidia-%{nvidia_branch}-load-open-gpu-kernel-modules.service
%if "%{_cross_arch}" == "x86_64"
%{_cross_unitdir}/nvidia-%{nvidia_branch}-copy-grid-kernel-modules.service
%{_cross_unitdir}/nvidia-%{nvidia_branch}-load-grid-kernel-modules.service
%endif

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
%dir %{nvidia_datadir}/nvidia/tesla/nvswitch
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgxa100_hgxa100_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgx2_hgx2_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgxh100_hgxh100_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgxh800_hgxh800_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgxgh200_hgxgh200_16gpus_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgxgh200_hgxgh200_32gpus_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/dgxgh200_hgxgh200_8gpus_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl36r1_c2g2_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl36r1_c2g4_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl4r1_c2g2_etf_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl576r16_c2g4_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl72r1_c2g4_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl72r2_c2g2_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl72r2_c2g4_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl8r1_c2g4_etf_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb200_nvl8r1_c2g4_etf_nso_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb300_nvl72r1_c2g4_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gb300_nvl72r2_c2g4_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/gh200_nvlink_32gpus_topology
%{nvidia_datadir}/nvidia/tesla/nvswitch/mgxh20_nvl16_topology

# Configuration files
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-tesla.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-open-gpu.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-open-gpu-copy-only.toml
%if "%{_cross_arch}" == "x86_64"
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-grid.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-%{nvidia_branch}-grid-copy-only.toml
%endif
%{nvidia_datadir}/nvidia/open-gpu-supported-devices.json

# driver
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia.mod.o
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nv-interface.o
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nv-kernel.o
%{nvidia_datadir}/nvidia/tesla/module-objects.d/.module-common.o

# uvm
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-uvm.mod.o
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-uvm.o

# modeset
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nv-modeset-interface.o
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nv-modeset-kernel.o
%{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-modeset.mod.o

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
%{nvidia_datadir}/egl/egl_external_platform.d/10_nvidia_wayland.json
%{nvidia_datadir}/egl/egl_external_platform.d/15_nvidia_gbm.json

# We only install the libraries required by all the DRIVER_CAPABILITIES, described here:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html#driver-capabilities

# Utility libs
%{nvidia_libdir}/libnvidia-api.so.1
%{nvidia_libdir}/libnvidia-ml.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-ml.so.1
%{nvidia_libdir}/libnvidia-cfg.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-cfg.so.1
%{nvidia_libdir}/libnvidia-nvvm.so.4
%{nvidia_libdir}/libnvidia-nvvm.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-nvvm70.so.4

# Compute libs
%{nvidia_libdir}/libcuda.so.%{tesla_ver}
%{nvidia_libdir}/libcuda.so.1
%{nvidia_libdir}/libcudadebugger.so.%{tesla_ver}
%{nvidia_libdir}/libcudadebugger.so.1
%{nvidia_libdir}/libnvidia-opencl.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-opencl.so.1
%{nvidia_libdir}/libnvidia-ptxjitcompiler.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-ptxjitcompiler.so.1
%{nvidia_libdir}/libnvidia-allocator.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-allocator.so.1
%{nvidia_libdir}/libOpenCL.so.1.0.0
%{nvidia_libdir}/libOpenCL.so.1
%{nvidia_libdir}/libnvidia-gpucomp.so.%{tesla_ver}
%if "%{_cross_arch}" == "x86_64"
%{nvidia_libdir}/libnvidia-pkcs11.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-pkcs11-openssl3.so.%{tesla_ver}
%endif

# Video libs
%{nvidia_libdir}/libvdpau_nvidia.so.%{tesla_ver}
%{nvidia_libdir}/libvdpau_nvidia.so.1
%{nvidia_libdir}/libnvidia-encode.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-encode.so.1
%{nvidia_libdir}/libnvidia-opticalflow.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-opticalflow.so.1
%{nvidia_libdir}/libnvcuvid.so.%{tesla_ver}
%{nvidia_libdir}/libnvcuvid.so.1

# Graphics libs
%{nvidia_libdir}/libnvidia-eglcore.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-glcore.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-tls.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-glsi.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-rtcore.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-fbc.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-fbc.so.1
%{nvidia_libdir}/libnvoptix.so.%{tesla_ver}
%{nvidia_libdir}/libnvoptix.so.1
%{nvidia_datadir}/nvidia/nvoptix.bin

# Graphics GLVND libs
%{nvidia_libdir}/libnvidia-glvkspirv.so.%{tesla_ver}
%{nvidia_libdir}/libGLX_nvidia.so.%{tesla_ver}
%{nvidia_libdir}/libGLX_nvidia.so.0
%{nvidia_libdir}/libEGL_nvidia.so.%{tesla_ver}
%{nvidia_libdir}/libEGL_nvidia.so.0
%{nvidia_libdir}/libGLESv2_nvidia.so.%{tesla_ver}
%{nvidia_libdir}/libGLESv2_nvidia.so.2
%{nvidia_libdir}/libGLESv1_CM_nvidia.so.%{tesla_ver}
%{nvidia_libdir}/libGLESv1_CM_nvidia.so.1
%if "%{_cross_arch}" == "x86_64"
%{nvidia_libdir}/libnvidia-present.so.%{tesla_ver}
%endif

# Graphics compat
%{nvidia_libdir}/libEGL.so.1.1.0
%{nvidia_libdir}/libEGL.so.1
%{nvidia_libdir}/libEGL.so.%{tesla_ver}
%{nvidia_libdir}/libGL.so.1.7.0
%{nvidia_libdir}/libGL.so.1
%{nvidia_libdir}/libGLESv1_CM.so.1.2.0
%{nvidia_libdir}/libGLESv1_CM.so.1
%{nvidia_libdir}/libGLESv2.so.2.1.0
%{nvidia_libdir}/libGLESv2.so.2

# NGX
%{nvidia_libdir}/libnvidia-ngx.so.%{tesla_ver}
%{nvidia_libdir}/libnvidia-ngx.so.1

# Firmware
%{_cross_libdir}/firmware/nvidia/%{tesla_ver}/gsp_ga10x.bin
%{_cross_libdir}/firmware/nvidia/%{tesla_ver}/gsp_tu10x.bin

# Neither nvidia-peermem nor nvidia-drm are included in driver container images, we exclude them
# for now, and we will add them if requested
%exclude %{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-peermem.mod.o
%exclude %{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-peermem.o
%exclude %{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-drm.mod.o
%exclude %{nvidia_datadir}/nvidia/tesla/module-objects.d/nvidia-drm.o
%if "%{_cross_arch}" == "x86_64"
%exclude %{_cross_libexecdir}/nvidia/%{nvidia_branch}/tesla/bin/nvidia-ngx-updater
%exclude %{nvidia_bindir}/nvidia-ngx-updater
%endif

# None of these libraries are required by libnvidia-container, so they
# won't be used by a containerized workload
%exclude %{nvidia_libdir}/libGLX.so.0
%exclude %{nvidia_libdir}/libGLdispatch.so.0
%exclude %{nvidia_libdir}/libOpenGL.so.0
%exclude %{nvidia_libdir}/libglxserver_nvidia.so.%{tesla_ver}
%exclude %{nvidia_libdir}/libnvidia-gtk2.so.%{tesla_ver}
%exclude %{nvidia_libdir}/libnvidia-gtk3.so.%{tesla_ver}
%exclude %{nvidia_libdir}/nvidia_drv.so
%exclude %{nvidia_libdir}/libnvidia-egl-wayland.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-gbm.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-gbm.so.1.1.3
%exclude %{nvidia_libdir}/libnvidia-egl-wayland.so.1.1.20
%exclude %{nvidia_libdir}/libnvidia-egl-xcb.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-xcb.so.1.0.5
%exclude %{nvidia_libdir}/libnvidia-egl-xlib.so.1
%exclude %{nvidia_libdir}/libnvidia-egl-xlib.so.1.0.5
%exclude %{nvidia_libdir}/libnvidia-sandboxutils.so.1
%exclude %{nvidia_libdir}/libnvidia-sandboxutils.so.%{tesla_ver}
%if "%{_cross_arch}" == "x86_64"
%exclude %{nvidia_libdir}/libnvidia-vksc-core.so.1
%exclude %{nvidia_libdir}/libnvidia-vksc-core.so.%{tesla_ver}
%exclude %{nvidia_libdir}/libnvidia-wayland-client.so.%{tesla_ver}
%endif

%files open-gpu
%license COPYING
%dir %{nvidia_datadir}/nvidia/open-gpu/drivers
%dir %{_cross_factorydir}/nvidia/%{nvidia_branch}/open-gpu

%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-uvm.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-modeset.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-drm.ko
%{nvidia_datadir}/nvidia/open-gpu/drivers/nvidia-peermem.ko

# GRID driver files
%if "%{_cross_arch}" == "x86_64"
%files grid
%license COPYING
%license NvidiaGridAWSUserLicenseAgreement.DOCX
%license NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws/grid-third-party-licenses.txt
%dir %{nvidia_datadir}/nvidia/grid/drivers
%dir %{_cross_factorydir}/nvidia/%{nvidia_branch}/grid
%{nvidia_bindir}/nvidia-gridd
%{nvidia_sysconfdir}/nvidia/gridd.conf
%{_cross_unitdir}/nvidia-gridd.service
%{_cross_unitdir}/grid-license-check.service
%{_cross_unitdir}/grid-license-check.timer
%{_cross_unitdir}/open-gpu-license-fallback.service
%{_cross_unitdir}/tesla-license-fallback.service
%{_cross_unitdir}/nvidia-k8s-device-plugin.service.d/grid-license-file-check.conf

%{nvidia_datadir}/nvidia/grid/drivers/nvidia.ko
%{nvidia_datadir}/nvidia/grid/drivers/nvidia-uvm.ko
%{nvidia_datadir}/nvidia/grid/drivers/nvidia-modeset.ko
%{nvidia_datadir}/nvidia/grid/drivers/nvidia-drm.ko
%{nvidia_datadir}/nvidia/grid/drivers/nvidia-peermem.ko
%endif

%files fabricmanager
%{nvidia_sysconfdir}/nvidia/fabricmanager.cfg
%{nvidia_sysconfdir}/nvidia/fabricmanager.env
%{_cross_unitdir}/nvidia-fabricmanager.service

%files imex
%{nvidia_bindir}/nvidia-imex
%{nvidia_bindir}/nvidia-imex-ctl
%{_cross_unitdir}/nvidia-imex.service
%{nvidia_sysconfdir}/nvidia-imex/config.cfg
%{_cross_tmpfilesdir}/nvidia-imex.conf

%files imex-config
%{_cross_libdir}/modprobe.d/10-nvidia-default-imex-channel.conf

%files mps
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
