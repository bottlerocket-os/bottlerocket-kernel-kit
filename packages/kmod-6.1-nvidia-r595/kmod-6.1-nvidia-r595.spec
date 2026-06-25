%global tesla_major 595
%global tesla_minor 71
%global tesla_patch 05
%global tesla_ver %{tesla_major}.%{tesla_minor}.%{tesla_patch}
%global grid_ver grid-20.1
%if "%{?_cross_arch}" == "aarch64"
%global nvidia_arch sbsa
%else
%global nvidia_arch %{_cross_arch}
%endif

# With the split of the firmware binary from firmware/gsp.bin to firmware/gsp_ga10x.bin
# and firmware/gsp_tu10x.bin the file format changed from executable to relocatable.
# The __spec_install_post macro will by default try to strip all binary files.
# Unfortunately the strip used is not compatible with the new file format.
# Redefine strip, so that these firmware binaries do not derail the build.
%global __strip /usr/bin/true

Name: %{_cross_os}kmod-6.1-nvidia-r595
Version: %{tesla_ver}
Release: 1%{?dist}
Epoch: 1
Summary: NVIDIA r595 drivers for the 6.1 kernel
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

# NVIDIA tesla conf files from 300 to 399
Source300: nvidia-tesla-tmpfiles.conf
Source301: nvidia-tesla-build-config.toml.in

# Driverdog config templates from 400 to 499
Source400: nvidia-open-gpu-config.toml.in
Source401: nvidia-open-gpu-copy-only-config.toml.in
Source402: nvidia-grid-config.toml.in
Source403: nvidia-grid-copy-only-config.toml.in

# Systemd service templates from 500 to 599
Source500: link-tesla-kernel-modules.service.in
Source501: load-tesla-kernel-modules.service.in
Source502: copy-open-gpu-kernel-modules.service.in
Source503: load-open-gpu-kernel-modules.service.in
Source504: copy-grid-kernel-modules.service.in
Source505: load-grid-kernel-modules.service.in

Patch001: 0001-makefile-allow-to-use-any-kernel-arch.patch

BuildRequires: %{_cross_os}kernel-6.1-archive
Requires: %{_cross_os}kernel-6.1
Requires: %{_cross_os}nvidia-migmanager
Requires: %{name}-tesla
Requires: %{name}-open-gpu
%if "%{_cross_arch}" == "x86_64"
Requires: %{name}-grid
%endif
Requires: %{name}-mps

%description
%{summary}.

%package fabricmanager
Summary: NVIDIA fabricmanager config and service files
Requires: %{name}-tesla(fabricmanager)
Requires: %{_cross_os}nvlsm

%description fabricmanager
%{summary}.

%package open-gpu
Summary: NVIDIA %{tesla_major} Open GPU driver
Version: %{tesla_ver}
License: MIT AND GPL-2.0-only
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}

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

%description grid
%{summary}.
%endif

%package tesla
Summary: NVIDIA %{tesla_major} Tesla driver
Version: %{tesla_ver}
License: LicenseRef-NVIDIA-AWS-EULA
Requires: %{_cross_os}variant-platform(aws)
Requires: %{name}
Requires: %{name}-fabricmanager
Provides: %{name}-tesla(fabricmanager)

%description tesla
%{summary}

%package mps
Summary: NVIDIA CUDA Multi-Process Service
Requires: %{name}

%description mps
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

%global kernel_sources %{_builddir}/kernel-devel
tar -xf %{_cross_datadir}/bottlerocket/kernel-devel.tar.xz

# This recipe was based in the NVIDIA yum/dnf specs:
# https://github.com/NVIDIA/yum-packaging-precompiled-kmod

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
and .devid != "0x1DEB8"
and .devid != "0x1EB4"
and .devid != "0x2237")' supported-gpus.json | jq -s '{"open-gpu": .}' > open-gpu-supported-devices.json
# confirm "NVIDIA H100" is in the resulting file to catch shape changes
jq -e '."open-gpu"[] | select(."devid" == "0x2330") | ."features"| index("kernelopen")' open-gpu-supported-devices.json
popd

%install
install -d %{buildroot}%{_cross_libdir}
install -d %{buildroot}%{_cross_libdir}/nvidia/tesla
install -d %{buildroot}%{_cross_tmpfilesdir}
install -d %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{_cross_sysusersdir}
install -d %{buildroot}%{_cross_bindir}

KERNEL_VERSION=$(cat %{kernel_sources}/include/config/kernel.release)
sed \
  -e "s|__KERNEL_VERSION__|${KERNEL_VERSION}|" \
  -e "s|__PREFIX__|%{_cross_prefix}|" %{S:200} > nvidia.conf
install -p -m 0644 nvidia.conf %{buildroot}%{_cross_tmpfilesdir}

# Install modules-load.d drop-in to autoload required kernel modules
install -d %{buildroot}%{_cross_libdir}/modules-load.d
install -p -m 0644 %{S:202} %{buildroot}%{_cross_libdir}/modules-load.d/nvidia-dependencies.conf

# NVIDIA fabric manager service unit and config
install -p -m 0644 %{S:203} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/nvidia
install -d %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
install -p -m 0644 %{S:204} %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/nvidia/fabricmanager.cfg
install -p -m 0644 %{S:207} %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/nvidia/fabricmanager.env

# Begin NVIDIA tesla driver
pushd NVIDIA-Linux-%{_cross_arch}-%{tesla_ver}
# Proprietary driver
install -d %{buildroot}%{_cross_bindir}
install -d %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin
install -d %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install -d %{buildroot}%{_cross_factorydir}/nvidia/tesla
install -d %{buildroot}%{_cross_factorydir}/nvidia/open-gpu
%if "%{_cross_arch}" == "x86_64"
install -d %{buildroot}%{_cross_factorydir}/nvidia/grid
%endif
install -d %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers

install -m 0644 %{S:300} %{buildroot}%{_cross_tmpfilesdir}/nvidia-tesla.conf
sed -e 's|__NVIDIA_MODULES__|%{_cross_datadir}/nvidia/tesla/module-objects.d/|' %{S:301} > \
  nvidia-tesla.toml
install -m 0644 nvidia-tesla.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{_cross_datadir}/nvidia/open-gpu/drivers/|' %{S:400} > \
  nvidia-open-gpu.toml
install -m 0644 nvidia-open-gpu.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{_cross_datadir}/nvidia/open-gpu/drivers/|' %{S:401} > \
  nvidia-open-gpu-copy-only.toml
install -m 0644 nvidia-open-gpu-copy-only.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers

%if "%{_cross_arch}" == "x86_64"
sed -e 's|__NVIDIA_MODULES__|%{_cross_datadir}/nvidia/grid/drivers/|' %{S:402} > \
  nvidia-grid.toml
install -m 0644 nvidia-grid.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
sed -e 's|__NVIDIA_MODULES__|%{_cross_datadir}/nvidia/grid/drivers/|' %{S:403} > \
  nvidia-grid-copy-only.toml
install -m 0644 nvidia-grid-copy-only.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
%endif
# Services to link/copy/load modules
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:500} > link-tesla-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:501} > load-tesla-kernel-modules.service
install -p -m 0644 \
  link-tesla-kernel-modules.service \
  load-tesla-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}

sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:502} > copy-open-gpu-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:503} > load-open-gpu-kernel-modules.service
install -p -m 0644 \
  copy-open-gpu-kernel-modules.service \
  load-open-gpu-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}

%if "%{_cross_arch}" == "x86_64"
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:504} > copy-grid-kernel-modules.service
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:505} > load-grid-kernel-modules.service
install -p -m 0644 \
  copy-grid-kernel-modules.service \
  load-grid-kernel-modules.service \
  %{buildroot}%{_cross_unitdir}
%endif

# proprietary driver
install kernel/nvidia.mod.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia/nv-interface.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia/nv-kernel.o_binary %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d/nv-kernel.o

# uvm
install kernel/nvidia-uvm.mod.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-uvm.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d

# modeset
install kernel/nvidia-modeset.mod.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-modeset/nv-modeset-interface.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-modeset/nv-modeset-kernel.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d

# peermem
install kernel/nvidia-peermem.mod.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-peermem/nvidia-peermem.o %{buildroot}%{_cross_datadir}/nvidia/tesla/module-objects.d

# drm
install kernel/nvidia-drm.mod.o %{buildroot}/%{_cross_datadir}/nvidia/tesla/module-objects.d
install kernel/nvidia-drm.o %{buildroot}/%{_cross_datadir}/nvidia/tesla/module-objects.d

# open driver
install -d %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers/
install kernel-open/nvidia.ko %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers/

# uvm
install kernel-open/nvidia-uvm.ko %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers/

# modeset
install kernel-open/nvidia-modeset.ko %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers/

# peermem
install kernel-open/nvidia-peermem.ko %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers/

# drm
install kernel-open/nvidia-drm.ko %{buildroot}%{_cross_datadir}/nvidia/open-gpu/drivers/
# end open driver

# add various vulkan icd/config
install -d %{buildroot}%{_cross_datadir}/vulkan/icd.d
install -d %{buildroot}%{_cross_datadir}/vulkan/implicit_layer.d
install -m 0644 nvidia_icd.json %{buildroot}%{_cross_datadir}/vulkan/icd.d/nvidia_icd.json
install -m 0644 nvidia_layers.json %{buildroot}%{_cross_datadir}/vulkan/icd.d/nvidia_layers.json
install -d %{buildroot}%{_cross_datadir}/glvnd/egl_vendor.d
install -m 0644 10_nvidia.json %{buildroot}%{_cross_datadir}/glvnd/egl_vendor.d/10_nvidia.json
install -d %{buildroot}%{_cross_datadir}/egl/egl_external_platform.d
install -m 0644 10_nvidia_wayland.json %{buildroot}%{_cross_datadir}/egl/egl_external_platform.d/10_nvidia_wayland.json
install -m 0644 15_nvidia_gbm.json %{buildroot}%{_cross_datadir}/egl/egl_external_platform.d/15_nvidia_gbm.json
ln -rs %{buildroot}%{_cross_datadir}/vulkan/icd.d/nvidia_layers.json %{buildroot}%{_cross_datadir}/vulkan/implicit_layer.d/nvidia_layers.json

%if "%{_cross_arch}" == "x86_64"
# GRID driver
pushd ../NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws
install -d %{buildroot}%{_cross_datadir}/nvidia/grid/drivers/
install kernel-open/nvidia.ko %{buildroot}%{_cross_datadir}/nvidia/grid/drivers/

# uvm
install kernel-open/nvidia-uvm.ko %{buildroot}%{_cross_datadir}/nvidia/grid/drivers/

# modeset
install kernel-open/nvidia-modeset.ko %{buildroot}%{_cross_datadir}/nvidia/grid/drivers/

# peermem
install kernel-open/nvidia-peermem.ko %{buildroot}%{_cross_datadir}/nvidia/grid/drivers/

# drm
install kernel-open/nvidia-drm.ko %{buildroot}%{_cross_datadir}/nvidia/grid/drivers/

# Install nvidia-gridd and related files
install -m 755 nvidia-gridd %{buildroot}%{_cross_bindir}/nvidia-gridd
install -m 644 %{S:208} %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/nvidia/gridd.conf
install -p -m 0644 %{S:209} %{S:210} %{S:211} %{S:212} %{S:213} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{_cross_unitdir}/nvidia-k8s-device-plugin.service.d
install -p -m 0644 %{S:214} %{buildroot}%{_cross_unitdir}/nvidia-k8s-device-plugin.service.d
popd
# End GRID driver
%endif

# Binaries
install -m 755 nvidia-smi %{buildroot}%{_cross_bindir}
install -m 755 nvidia-debugdump %{buildroot}%{_cross_bindir}
install -m 755 nvidia-cuda-mps-control %{buildroot}%{_cross_bindir}
install -m 755 nvidia-cuda-mps-server %{buildroot}%{_cross_bindir}
install -m 755 nvidia-persistenced %{buildroot}%{_cross_bindir}
install -m 4755 nvidia-modprobe %{buildroot}%{_cross_bindir}
install -m 755 nvoptix.bin %{buildroot}%{_cross_datadir}/nvidia/
ln -rs %{buildroot}%{_cross_bindir}/nvidia-smi %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-smi
ln -rs %{buildroot}%{_cross_bindir}/nvidia-debugdump %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-debugdump
ln -rs %{buildroot}%{_cross_bindir}/nvidia-cuda-mps-control %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-cuda-mps-control
ln -rs %{buildroot}%{_cross_bindir}/nvidia-cuda-mps-server %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-cuda-mps-server
ln -rs %{buildroot}%{_cross_bindir}/nvidia-persistenced %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-persistenced
%if "%{_cross_arch}" == "x86_64"
install -m 755 nvidia-ngx-updater %{buildroot}%{_cross_bindir}
ln -rs %{buildroot}%{_cross_bindir}/nvidia-ngx-updater %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-ngx-updater
%endif

# Users
install -m 0644 %{S:205} %{buildroot}%{_cross_sysusersdir}/nvidia.conf

# Systemd units
install -m 0644 %{S:206} %{buildroot}%{_cross_unitdir}

# We install all the libraries, and filter them out in the 'files' section,
# so we can catch when new libraries are added
install -m 755 *.so* %{buildroot}/%{_cross_libdir}/

# This library has the same SONAME as libEGL.so.1.1.0, this will cause
# collisions while the symlinks are created. For now, we only symlink
# libEGL.so.1.1.0.
EXCLUDED_LIBS="libEGL.so.%{tesla_ver}"

for lib in $(find . -maxdepth 1 -type f -name 'lib*.so.*' -printf '%%P\n'); do
  [[ "${EXCLUDED_LIBS}" =~ "${lib}" ]] && continue
  # Create backwards-compatibility symlink in nvidia/tesla/
  ln -rs "%{buildroot}/%{_cross_libdir}/${lib}" "%{buildroot}/%{_cross_libdir}/nvidia/tesla/${lib}"
  soname="$(%{_cross_target}-readelf -d "${lib}" | awk '/SONAME/{print $5}' | tr -d '[]')"
  [ -n "${soname}" ] || continue
  [ "${lib}" == "${soname}" ] && continue
  ln -s "${lib}" %{buildroot}/%{_cross_libdir}/"${soname}"
done

# Include the firmware file for GSP support
install -d %{buildroot}%{_cross_libdir}/firmware/nvidia/%{tesla_ver}
install -p -m 0644 firmware/gsp_ga10x.bin %{buildroot}%{_cross_libdir}/firmware/nvidia/%{tesla_ver}
install -p -m 0644 firmware/gsp_tu10x.bin %{buildroot}%{_cross_libdir}/firmware/nvidia/%{tesla_ver}

# Include the open driver supported devices file for runtime matching of the
# driver. This is consumed by ghostdog to match the driver to this list
install -p -m 0644 supported-gpus/open-gpu-supported-devices.json %{buildroot}%{_cross_datadir}/nvidia/open-gpu-supported-devices.json

popd

# Begin NVIDIA fabric manager binaries and topologies
pushd fabricmanager-linux-%{nvidia_arch}-%{tesla_ver}-archive
install -p -m 0755 usr/bin/nv-fabricmanager %{buildroot}%{_cross_bindir}
install -p -m 0755 usr/bin/nvswitch-audit %{buildroot}%{_cross_bindir}
ln -rs %{buildroot}%{_cross_bindir}/nv-fabricmanager %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nv-fabricmanager
ln -rs %{buildroot}%{_cross_bindir}/nvswitch-audit %{buildroot}%{_cross_libexecdir}/nvidia/tesla/bin/nvswitch-audit

install -d %{buildroot}%{_cross_datadir}/nvidia/tesla/nvswitch
for t in usr/share/nvidia/nvswitch/*_topology ; do
  install -p -m 0644 "${t}" %{buildroot}%{_cross_datadir}/nvidia/tesla/nvswitch
done

popd

%files
%{_cross_attribution_file}
%dir %{_cross_libexecdir}/nvidia
%dir %{_cross_libdir}/nvidia
%dir %{_cross_datadir}/nvidia
%dir %{_cross_libdir}/modules-load.d
%dir %{_cross_factorydir}%{_cross_sysconfdir}/drivers
%dir %{_cross_factorydir}%{_cross_sysconfdir}/nvidia
%{_cross_tmpfilesdir}/nvidia.conf
%{_cross_libdir}/modules-load.d/nvidia-dependencies.conf

%files tesla
%license NVidiaEULAforAWS.pdf
%license fabricmanager-linux-%{nvidia_arch}-%{tesla_ver}-archive/usr/share/licenses/nvidia-fabricmanager/third-party-notices.txt
%dir %{_cross_datadir}/egl
%dir %{_cross_datadir}/egl/egl_external_platform.d
%dir %{_cross_datadir}/glvnd
%dir %{_cross_datadir}/glvnd/egl_vendor.d
%dir %{_cross_datadir}/nvidia/tesla
%dir %{_cross_datadir}/nvidia/tesla/module-objects.d
%dir %{_cross_datadir}/vulkan
%dir %{_cross_datadir}/vulkan/icd.d
%dir %{_cross_datadir}/vulkan/implicit_layer.d
%dir %{_cross_factorydir}/nvidia/tesla
%dir %{_cross_libdir}/firmware/nvidia/%{tesla_ver}
%dir %{_cross_libdir}/nvidia/tesla
%{_cross_libdir}/nvidia/tesla/*
%dir %{_cross_libexecdir}/nvidia/tesla/bin
%{_cross_unitdir}/link-tesla-kernel-modules.service
%{_cross_unitdir}/load-tesla-kernel-modules.service
%{_cross_unitdir}/copy-open-gpu-kernel-modules.service
%{_cross_unitdir}/load-open-gpu-kernel-modules.service
%if "%{_cross_arch}" == "x86_64"
%{_cross_unitdir}/copy-grid-kernel-modules.service
%{_cross_unitdir}/load-grid-kernel-modules.service
%endif

# Binaries
%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-debugdump
%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-smi
%{_cross_libexecdir}/nvidia/tesla/bin/nv-fabricmanager
%{_cross_libexecdir}/nvidia/tesla/bin/nvswitch-audit
%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-persistenced
%{_cross_bindir}/nvidia-debugdump
%{_cross_bindir}/nvidia-smi
%{_cross_bindir}/nv-fabricmanager
%{_cross_bindir}/nvswitch-audit
%{_cross_bindir}/nvidia-persistenced
%{_cross_bindir}/nvidia-modprobe

# nvswitch topologies
%dir %{_cross_datadir}/nvidia/tesla/nvswitch
%{_cross_datadir}/nvidia/tesla/nvswitch/dgxa100_hgxa100_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/dgx2_hgx2_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/dgxh100_hgxh100_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/dgxh800_hgxh800_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/dgxgh200_hgxgh200_16gpus_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/dgxgh200_hgxgh200_32gpus_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/dgxgh200_hgxgh200_8gpus_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl36r1_c2g2_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl36r1_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl4r1_c2g2_etf_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl576r16_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl576r4_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl72r1_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl72r2_c2g2_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl72r2_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl8r1_c2g4_etf_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb200_nvl8r1_c2g4_etf_nso_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb300_nvl72r1_c2g4_kyber_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb300_nvl72r1_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gb300_nvl72r2_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/gh200_nvlink_32gpus_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/mgxh20_nvl16_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/vr_nvl144r1_c2g4_topology
%{_cross_datadir}/nvidia/tesla/nvswitch/vr_nvl16r1_c2g4_rtf_topology

# Configuration files
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-tesla.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-open-gpu.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-open-gpu-copy-only.toml
%if "%{_cross_arch}" == "x86_64"
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-grid.toml
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/nvidia-grid-copy-only.toml
%endif
%{_cross_datadir}/nvidia/open-gpu-supported-devices.json

# driver
%{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia.mod.o
%{_cross_datadir}/nvidia/tesla/module-objects.d/nv-interface.o
%{_cross_datadir}/nvidia/tesla/module-objects.d/nv-kernel.o

# uvm
%{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-uvm.mod.o
%{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-uvm.o

# modeset
%{_cross_datadir}/nvidia/tesla/module-objects.d/nv-modeset-interface.o
%{_cross_datadir}/nvidia/tesla/module-objects.d/nv-modeset-kernel.o
%{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-modeset.mod.o

# tmpfiles
%{_cross_tmpfilesdir}/nvidia-tesla.conf

# sysuser files
%{_cross_sysusersdir}/nvidia.conf

# systemd units
%{_cross_unitdir}/nvidia-persistenced.service

# ICD / vendor descriptors
%{_cross_datadir}/vulkan/icd.d/nvidia_icd.json
%{_cross_datadir}/vulkan/icd.d/nvidia_layers.json
%{_cross_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%{_cross_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%{_cross_datadir}/egl/egl_external_platform.d/10_nvidia_wayland.json
%{_cross_datadir}/egl/egl_external_platform.d/15_nvidia_gbm.json

# We only install the libraries required by all the DRIVER_CAPABILITIES, described here:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html#driver-capabilities

# Utility libs
%{_cross_libdir}/libnvidia-api.so.1
%{_cross_libdir}/libnvidia-ml.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-ml.so.1
%{_cross_libdir}/libnvidia-cfg.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-cfg.so.1
%{_cross_libdir}/libnvidia-nvvm.so.4
%{_cross_libdir}/libnvidia-nvvm.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-nvvm70.so.4

# Compute libs
%{_cross_libdir}/libcuda.so.%{tesla_ver}
%{_cross_libdir}/libcuda.so.1
%{_cross_libdir}/libcudadebugger.so.%{tesla_ver}
%{_cross_libdir}/libcudadebugger.so.1
%{_cross_libdir}/libnvidia-opencl.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-opencl.so.1
%{_cross_libdir}/libnvidia-ptxjitcompiler.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-ptxjitcompiler.so.1
%{_cross_libdir}/libnvidia-allocator.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-allocator.so.1
%{_cross_libdir}/libOpenCL.so.1.0.0
%{_cross_libdir}/libOpenCL.so.1
%{_cross_libdir}/libnvidia-gpucomp.so.%{tesla_ver}
%if "%{_cross_arch}" == "x86_64"
%{_cross_libdir}/libnvidia-pkcs11.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-pkcs11-openssl3.so.%{tesla_ver}
%endif

# Video libs
%{_cross_libdir}/libvdpau_nvidia.so.%{tesla_ver}
%{_cross_libdir}/libvdpau_nvidia.so.1
%{_cross_libdir}/libnvidia-encode.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-encode.so.1
%{_cross_libdir}/libnvidia-opticalflow.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-opticalflow.so.1
%{_cross_libdir}/libnvcuvid.so.%{tesla_ver}
%{_cross_libdir}/libnvcuvid.so.1

# Graphics libs
%{_cross_libdir}/libnvidia-egl-wayland2.so.1
%{_cross_libdir}/libnvidia-egl-wayland2.so.1.0.1
%{_cross_libdir}/libnvidia-eglcore.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-glcore.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-tls.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-glsi.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-rtcore.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-tileiras.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-fbc.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-fbc.so.1
%{_cross_libdir}/libnvoptix.so.%{tesla_ver}
%{_cross_libdir}/libnvoptix.so.1
%{_cross_datadir}/nvidia/nvoptix.bin

# Graphics GLVND libs
%{_cross_libdir}/libnvidia-glvkspirv.so.%{tesla_ver}
%{_cross_libdir}/libGLX_nvidia.so.%{tesla_ver}
%{_cross_libdir}/libGLX_nvidia.so.0
%{_cross_libdir}/libEGL_nvidia.so.%{tesla_ver}
%{_cross_libdir}/libEGL_nvidia.so.0
%{_cross_libdir}/libGLESv2_nvidia.so.%{tesla_ver}
%{_cross_libdir}/libGLESv2_nvidia.so.2
%{_cross_libdir}/libGLESv1_CM_nvidia.so.%{tesla_ver}
%{_cross_libdir}/libGLESv1_CM_nvidia.so.1
%{_cross_libdir}/libnvidia-present.so.%{tesla_ver}

# Graphics compat
%{_cross_libdir}/libEGL.so.1.1.0
%{_cross_libdir}/libEGL.so.1
%{_cross_libdir}/libEGL.so.%{tesla_ver}
%{_cross_libdir}/libGL.so.1.7.0
%{_cross_libdir}/libGL.so.1
%{_cross_libdir}/libGLESv1_CM.so.1.2.0
%{_cross_libdir}/libGLESv1_CM.so.1
%{_cross_libdir}/libGLESv2.so.2.1.0
%{_cross_libdir}/libGLESv2.so.2

# NGX
%{_cross_libdir}/libnvidia-ngx.so.%{tesla_ver}
%{_cross_libdir}/libnvidia-ngx.so.1

# Firmware
%{_cross_libdir}/firmware/nvidia/%{tesla_ver}/gsp_ga10x.bin
%{_cross_libdir}/firmware/nvidia/%{tesla_ver}/gsp_tu10x.bin

# Neither nvidia-peermem nor nvidia-drm are included in driver container images, we exclude them
# for now, and we will add them if requested
%exclude %{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-peermem.mod.o
%exclude %{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-peermem.o
%exclude %{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-drm.mod.o
%exclude %{_cross_datadir}/nvidia/tesla/module-objects.d/nvidia-drm.o

%if "%{_cross_arch}" == "x86_64"
%exclude %{_cross_libexecdir}/nvidia/tesla/bin/nvidia-ngx-updater
%exclude %{_cross_bindir}/nvidia-ngx-updater
%endif

# None of these libraries are required by libnvidia-container, so they
# won't be used by a containerized workload
%exclude %{_cross_libdir}/libGLX.so.0
%exclude %{_cross_libdir}/libGLdispatch.so.0
%exclude %{_cross_libdir}/libOpenGL.so.0
%exclude %{_cross_libdir}/libglxserver_nvidia.so.%{tesla_ver}
%exclude %{_cross_libdir}/libnvidia-gtk2.so.%{tesla_ver}
%exclude %{_cross_libdir}/libnvidia-gtk3.so.%{tesla_ver}
%exclude %{_cross_libdir}/nvidia_drv.so
%exclude %{_cross_libdir}/libnvidia-egl-wayland.so.1
%exclude %{_cross_libdir}/libnvidia-egl-gbm.so.1
%exclude %{_cross_libdir}/libnvidia-egl-gbm.so.1.1.3
%exclude %{_cross_libdir}/libnvidia-egl-wayland.so.1.1.20
%exclude %{_cross_libdir}/libnvidia-egl-xcb.so.1
%exclude %{_cross_libdir}/libnvidia-egl-xcb.so.1.0.5
%exclude %{_cross_libdir}/libnvidia-egl-xlib.so.1
%exclude %{_cross_libdir}/libnvidia-egl-xlib.so.1.0.5
%exclude %{_cross_libdir}/libnvidia-sandboxutils.so.1
%exclude %{_cross_libdir}/libnvidia-sandboxutils.so.%{tesla_ver}
%if "%{_cross_arch}" == "x86_64"
%exclude %{_cross_libdir}/libnvidia-vksc-core.so.1
%exclude %{_cross_libdir}/libnvidia-vksc-core.so.%{tesla_ver}
%exclude %{_cross_libdir}/libnvidia-wayland-client.so.%{tesla_ver}
%endif

%files open-gpu
%license COPYING
%dir %{_cross_datadir}/nvidia/open-gpu/drivers
%dir %{_cross_factorydir}/nvidia/open-gpu

%{_cross_datadir}/nvidia/open-gpu/drivers/nvidia.ko
%{_cross_datadir}/nvidia/open-gpu/drivers/nvidia-uvm.ko
%{_cross_datadir}/nvidia/open-gpu/drivers/nvidia-modeset.ko
%{_cross_datadir}/nvidia/open-gpu/drivers/nvidia-drm.ko
%{_cross_datadir}/nvidia/open-gpu/drivers/nvidia-peermem.ko

# GRID driver files
%if "%{_cross_arch}" == "x86_64"
%files grid
%license COPYING
%license NvidiaGridAWSUserLicenseAgreement.DOCX
%license NVIDIA-Linux-x86_64-%{tesla_ver}-grid-aws/grid-third-party-licenses.txt
%dir %{_cross_datadir}/nvidia/grid/drivers
%dir %{_cross_factorydir}/nvidia/grid
%{_cross_bindir}/nvidia-gridd
%{_cross_factorydir}%{_cross_sysconfdir}/nvidia/gridd.conf
%{_cross_unitdir}/nvidia-gridd.service
%{_cross_unitdir}/grid-license-check.service
%{_cross_unitdir}/grid-license-check.timer
%{_cross_unitdir}/open-gpu-license-fallback.service
%{_cross_unitdir}/tesla-license-fallback.service
%{_cross_unitdir}/nvidia-k8s-device-plugin.service.d/grid-license-file-check.conf

%{_cross_datadir}/nvidia/grid/drivers/nvidia.ko
%{_cross_datadir}/nvidia/grid/drivers/nvidia-uvm.ko
%{_cross_datadir}/nvidia/grid/drivers/nvidia-modeset.ko
%{_cross_datadir}/nvidia/grid/drivers/nvidia-drm.ko
%{_cross_datadir}/nvidia/grid/drivers/nvidia-peermem.ko
%endif

%files fabricmanager
%{_cross_factorydir}%{_cross_sysconfdir}/nvidia/fabricmanager.cfg
%{_cross_factorydir}%{_cross_sysconfdir}/nvidia/fabricmanager.env
%{_cross_unitdir}/nvidia-fabricmanager.service

%files mps
%{_cross_bindir}/nvidia-cuda-mps-control
%{_cross_bindir}/nvidia-cuda-mps-server
%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-cuda-mps-control
%{_cross_libexecdir}/nvidia/tesla/bin/nvidia-cuda-mps-server
