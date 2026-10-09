%global _cross_first_party 1
%global debug_package %{nil}

# This package is unusual for the repo: it has no Source0 and no %build. It
# exists only to install the shared kernel config fragments (below) into the
# build sysroot, where kernel-6.18 and kernel-6.18-microvm consume them via a
# build-dependency instead of each carrying its own copy.
Name: %{_cross_os}kernel-6.18-shared-configs
Version: 0.1
Release: 1%{?dist}
Summary: Shared Bottlerocket kernel configuration fragments for 6.18
License: Apache-2.0 OR MIT
URL: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/tree/develop/packages/kernel-6.18-shared-configs

# The base Bottlerocket kernel configuration fragments shared by every
# 6.18-based kernel package (kernel-6.18 and kernel-6.18-microvm).
Source100: config-bottlerocket
Source101: config-bottlerocket-x86_64
Source102: config-bottlerocket-aarch64

%global kernel_configdir %{_cross_datadir}/bottlerocket/kernel-configs

%description
%{summary}.

%prep

%build

%install
install -d %{buildroot}%{kernel_configdir}
install -p -m 0644 %{S:100} %{S:101} %{S:102} %{buildroot}%{kernel_configdir}

%files
%dir %{_cross_datadir}/bottlerocket
%dir %{kernel_configdir}
%{kernel_configdir}/config-bottlerocket
%{kernel_configdir}/config-bottlerocket-x86_64
%{kernel_configdir}/config-bottlerocket-aarch64

%changelog
