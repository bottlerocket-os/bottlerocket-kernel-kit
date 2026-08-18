%global efa_installer_ver 1.49.0
%global kernel_sources %{_cross_usrsrc}/kernels/6.12
%define _kernel_version %(cat %{kernel_sources}/include/config/kernel.release)
%global _cross_kmoddir %{_cross_libdir}/modules/%{_kernel_version}
%global _ko ko

Name: %{_cross_os}kmod-6.12-efa
Version: 3.0.0
Release: 1%{?dist}
Epoch: 1
Summary: EFA driver for the 6.12 kernel
License: MIT AND GPL-2.0-only AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0 OR Linux-OpenIB) AND (((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause))
URL: https://github.com/amzn/amzn-drivers

Source0: https://efa-installer.amazonaws.com/aws-efa-installer-%{efa_installer_ver}.tar.gz
Source1: COPYING
# Replace upstream CMakeLists.txt with one that allows overriding kernel paths.
Source2: EFACMakeLists.txt.in
Source100: load-efa-modules.service

BuildRequires: %{_cross_os}kernel-6.12-devel
Requires: %{_cross_os}kernel-6.12

%description
%{summary}.

%prep
tar -xf %{S:0}
rpm2cpio aws-efa-installer/RPMS/ALINUX2023/%{_cross_arch}/efa-driver/efa-*.%{_cross_arch}.rpm | cpio -idmu './usr/src/efa-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} efa_driver \;
rm -r aws-efa-installer
mkdir efa_driver/build
sed \
  -e "s|__KERNEL_DIR__|%{kernel_sources}|g" \
  -e "s|__KERNEL_MAKEFILE__|%{kernel_sources}/Makefile|g" %{S:2} > efa_driver/CMakeLists.txt

%global kmake %{shrink: \
make -s \
  ARCH="%{_cross_karch}" \
  CROSS_COMPILE="%{_cross_target}-" \
  INSTALL_HDR_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_STRIP=1 \
  %{nil}}

%build
# The modules_prepare command has to be called first to generate the tools required for
# the architecture of the host. Usually this is called by the modules target when the OOT
# module is compiled. However in the EFA driver CMAKE instructions, the `modules` target
# runs in parallel to test the configurations of the kernel which breaks for Bottlerocket's
# kernel devel sources.
%kmake -C %{kernel_sources} M=%{_builddir}/efa_driver/build modules_prepare

pushd %{_builddir}/efa_driver/build
# Mask the modules_prepare target to prevent the parallel tests execution from breaking
sed -i -e 's,$(MAKE),PREPARE=true %{kmake},g' ../config/Makefile
%{cross_cmake} ..
%kmake %{?_smp_mflags} M=%{_builddir}/efa_driver/build modules
popd

%install
install -p -m 0644 %{S:1} .
install -d %{buildroot}%{_cross_unitdir}
install -p -m 0644 %{S:100} %{buildroot}%{_cross_unitdir}
install -d %{buildroot}%{_cross_kmoddir}
%kmake -C %{kernel_sources} %{?_smp_mflags} \
  DEPMOD=true \
  M=%{_builddir}/efa_driver/build/src \
  INSTALL_MOD_DIR=updates/drivers/amazon/net/efa \
  modules_install

%files
%license COPYING
%{_cross_attribution_file}
%{_cross_unitdir}/load-efa-modules.service
%{_cross_kmoddir}/updates/drivers/amazon/net/efa/efa.%{_ko}
