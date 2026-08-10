%global debug_package %{nil}
%global __strip %{_bindir}/true

%global efidir /boot/efi/EFI/BOOT
%global grub_efi_image grub%{_cross_efi_arch}.efi
%global systemd_boot_efi_image systemd-boot%{_cross_efi_arch}.efi
%global shim_systemd_boot_efi_image shim-%{systemd_boot_efi_image}
%global shim_efi_image shim%{_cross_efi_arch}.efi
%global mokm_efi_image mm%{_cross_efi_arch}.efi

%global boot_efi_image boot%{_cross_efi_arch}.efi

%global shimver 16.0
%global commit 18d98bfb34be583a5fe2987542e4b15e0db9cb61

Name: %{_cross_os}shim
Version: %{shimver}
Release: 1%{?dist}
Summary: UEFI shim loader
License: BSD-3-Clause
URL: https://github.com/rhboot/shim/
Source0: https://github.com/rhboot/shim/releases/download/%{shimver}/shim-%{shimver}.tar.bz2
Source1: https://github.com/rhboot/shim/releases/download/%{shimver}/shim-%{shimver}.tar.bz2.asc
Source2: gpgkey-8107B101A432AAC9FE8E547CA348D61BC2713E9F.asc

Requires: %{name}(shim-efi)

%description
%{summary}.

%package grub
Summary: Shim built to chain-load GRUB
# Avoid explicit image-feature(no-uki-image) requires for backwards compatibility
# The conflict is enough for now to prevent installing GRUB when UKIs are used
Requires: %{name}
# The epoch here is a tie-breaker signaling this subpackage is the default
# shim-efi provider; selection is actually enforced by the Conflicts below.
Provides: %{name}(shim-efi) = 1:
Conflicts: %{_cross_os}image-feature(uki-image)
# Mutually exclusive with other shim providers
Conflicts: %{name}(shim-efi)

%description grub
%{summary}.

%package systemd-boot
Summary: Shim built to chain-load systemd-boot
Requires: %{name}
Requires: %{_cross_os}image-feature(uki-image)
# The epoch here is a tie-breaker signaling this subpackage is not the
# default shim-efi provider; selection is actually enforced by the
# Requires/Conflicts below.
Provides: %{name}(shim-efi) = 0:
Conflicts: %{_cross_os}image-feature(no-uki-image)
# Mutually exclusive with other shim providers
Conflicts: %{name}(shim-efi)

%description systemd-boot
%{summary}.

%prep
%{gpgverify} --data=%{S:0} --signature=%{S:1} --keyring=%{S:2}
%autosetup -n shim-%{shimver} -p1

# Make sure the `.vendor_cert` section is large enough to cover a replacement
# certificate, or `objcopy` may silently retain the existing section.
# 4096 - 16 (for cert_table structure) = 4080 bytes.
truncate -s 4080 empty.cer

%global shim_make \
make\\\
  ARCH="%{_cross_arch}"\\\
  CROSS_COMPILE="%{_cross_target}-"\\\
  COMMIT_ID="%{commit}"\\\
  RELEASE="%{release}"\\\
  DISABLE_REMOVABLE_LOAD_OPTIONS=y\\\
  DESTDIR="%{buildroot}"\\\
  EFIDIR="BOOT"\\\
  VENDOR_CERT_FILE="empty.cer"\\\
  POST_PROCESS_PE_FLAGS="-N"\\\
%{nil}

%build
# Build shim twice using separate source-tree copies. Building in-tree ensures
# DEFAULT_LOADER propagates correctly to the preprocessor defines.
cp -a %{_builddir}/shim-%{shimver} %{_builddir}/build-grub
cp -a %{_builddir}/shim-%{shimver} %{_builddir}/build-systemd-boot

cd %{_builddir}/build-grub
%shim_make DEFAULT_LOADER="%{grub_efi_image}"

cd %{_builddir}/build-systemd-boot
%shim_make DEFAULT_LOADER="%{systemd_boot_efi_image}"

%install
install -d %{buildroot}%{efidir}

# Install grub-chaining shim at the default boot path, for backwards
# compatibility with image builds that expect to find it there.
find %{_builddir}/build-grub -name '%{shim_efi_image}' -exec \
  cp {} "%{buildroot}%{efidir}/%{boot_efi_image}" \;

find %{_builddir}/build-systemd-boot -name '%{shim_efi_image}' -exec \
  cp {} "%{buildroot}%{efidir}/%{shim_systemd_boot_efi_image}" \;

# MokManager is not affected by DEFAULT_LOADER; either build tree is fine.
find %{_builddir}/build-grub -name '%{mokm_efi_image}' -exec \
  cp {} "%{buildroot}%{efidir}/%{mokm_efi_image}" \;

%files
%license COPYRIGHT
%{_cross_attribution_file}
%dir %{efidir}
%{efidir}/%{mokm_efi_image}

%files grub
%{efidir}/%{boot_efi_image}

%files systemd-boot
%{efidir}/%{shim_systemd_boot_efi_image}
