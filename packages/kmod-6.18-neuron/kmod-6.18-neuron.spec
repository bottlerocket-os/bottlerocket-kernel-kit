%global kmajor 6.18
%global kernel_sources %{_cross_usrsrc}/kernels/%{kmajor}
%global _cross_kmoddir %{_cross_libdir}/modules/%{kmajor}
%global _ko ko
%global neuron_ver 2.26.10
%global neuron_inf1_ver 2.24.13

Name: %{_cross_os}kmod-6.18-neuron
Version: %{neuron_ver}
Release: 1%{?dist}
Epoch: 1
Summary: Neuron drivers for the 6.18 kernel
License: Apache-2.0 OR MIT
URL: https://aws.amazon.com/ai/machine-learning/neuron/

# Use latest-2.24-neuron-srpm-url.sh to get this.
Source1: https://yum.repos.neuron.amazonaws.com/aws-neuronx-dkms-%{neuron_inf1_ver}.0.noarch.rpm
# Use latest-neuron-srpm-url.sh to get this.
Source2: https://yum.repos.neuron.amazonaws.com/aws-neuronx-dkms-%{neuron_ver}.0.noarch.rpm
# Neuron driver 2.x.7372.0
Source3: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.7372.0.noarch.rpm/e82516a77ab54f1c651a1f160e3a67b1cbca8bef391d78a6c683d6fc22442c8ee17df9d3fae1392ca8cffa676bb966b7088c32e634894ba142d83bef58dd2d81/aws-neuronx-dkms-2.x.7372.0.noarch.rpm
# Neuron driver 2.x.7693.0
Source4: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.7693.0.noarch.rpm/4411e3d28bc307bd096408f72f9c3d9e3edcadcbeab3ca409b0f94041ac1f589120353edfb1e11c45ff5a5421808297a308f18a6ac687459abe8c5e985653d3f/aws-neuronx-dkms-2.x.7693.0.noarch.rpm
# Neuron driver 2.x.8072.0
Source5: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.8072.0.noarch.rpm/d96bd0fe73482684c97faae6f779bfa8a84e9b9ca09f796031d409322550fb1744a38e6c54f5fcc8c1221f051cf04f518694876ea825722f5ed7895c2e8bb22a/aws-neuronx-dkms-2.x.8072.0.noarch.rpm
# Neuron driver 2.x.8689.0
Source6: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.8689.0.noarch.rpm/5d3ce7f81858d5aae62279369bce72e041dd321f71146a4ab8e61f9230f3965323f9c9230547476614f1c334b84c59edbd892524e2a87c35b46960a044502e9f/aws-neuronx-dkms-2.x.8689.0.noarch.rpm
# Neuron driver 2.x.8586.0
Source7: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.8586.0.noarch.rpm/0c5bf7f6ffd9d1ef3585aad48c8bb9a1f3f242e32af63755c3f914d9d000dc1f999b53ea90718dfbbfb8c3318ac80c0c90fc68a4962ea25ce4948183d62eb732/aws-neuronx-dkms-2.x.8586.0.noarch.rpm
# Neuron driver 2.x.8732.0
Source8: https://cache.bottlerocket.aws/aws-neuronx-dkms-2.x.8732.0.noarch.rpm/089caa0289ff37219583a2fcb7f947520da0c130595ff2a5917a04eed3d6272064332deb48a4b401fa0385b5450cc5fc3195991ca59b42a321d5706641f435e5/aws-neuronx-dkms-2.x.8732.0.noarch.rpm
Source9: gpgkey-00FA2C1079260870A76D2C285749CAD8646D9185.asc

# Neuron-related configuration and unit files
Source220: neuron-tmpfiles.conf
Source221: neuron-inf1.toml
Source222: load-neuron-inf1-modules.service
Source223: neuron-latest.toml
Source224: load-neuron-latest-modules.service

# Neuron driver patches for kernel 6.18 compatibility.
Patch2001: 2001-Rename-struct-mempool-to-struct-neuron_mempool.patch

BuildRequires: %{_cross_os}kernel-6.18-devel
Requires: %{_cross_os}kernel-6.18

Requires: %{_cross_os}ghostdog
Requires: %{_cross_os}variant-platform(aws)
Conflicts: %{_cross_os}variant-flavor(nvidia)
Conflicts: %{_cross_os}variant-flavor(nvidia-fips)

%description
%{summary}.

%package latest
Summary: Neuron %{version} driver
License: MIT AND GPL-2.0-only AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0 OR Linux-OpenIB) AND (((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause))
Requires: %{name}

%description latest
%{summary}.

%package inf1
Version: %{neuron_inf1_ver}
Summary: Neuron %{neuron_inf1_ver} driver
License: MIT AND GPL-2.0-only AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0 OR Linux-OpenIB) AND (((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause))
Requires: %{name}

%description inf1
%{summary}.

%package extras
Summary: Extra Neuron drivers
License: MIT AND GPL-2.0-only AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0 OR Linux-OpenIB) AND (((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause))
Requires: %{name}

%description extras
%{summary}.

%prep
rpmkeys --import %{S:9} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:1} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:2} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:3} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:4} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:5} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:6} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:7} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:8} --dbpath "${PWD}/rpmdb"
rm -rf "${PWD}/rpmdb"

rpm2cpio %{S:1} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2_24 \;
rm -r usr

rpm2cpio %{S:2} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_latest \;
rm -r usr

# 2.x.7372.0 neuron driver
rpm2cpio %{S:3} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_7372 \;
rm -r usr
pushd neuron_2x_7372
%patch -P 2001 -p1
popd

# 2.x.7693.0 neuron driver
rpm2cpio %{S:4} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_7693 \;
rm -r usr
pushd neuron_2x_7693
%patch -P 2001 -p1
popd

# 2.x.8072.0 neuron driver
rpm2cpio %{S:5} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_8072 \;
rm -r usr
pushd neuron_2x_8072
%patch -P 2001 -p1
popd

# 2.x.8689.0 neuron driver
rpm2cpio %{S:6} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_8689 \;
rm -r usr

# 2.x.8586.0 neuron driver
rpm2cpio %{S:7} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_8586 \;
rm -r usr

# 2.x.8732.0 neuron driver
rpm2cpio %{S:8} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron_2x_8732 \;
rm -r usr

%global kmake %{shrink: \
make -s \
  ARCH="%{_cross_karch}" \
  CROSS_COMPILE="%{_cross_target}-" \
  INSTALL_HDR_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_STRIP=1 \
  %{nil}}

%build
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2_24
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_latest
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_7372
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_7693
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_8072
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_8689
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_8586
%kmake -C %{kernel_sources} %{?_smp_mflags} M=%{_builddir}/neuron_2x_8732

%install
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2_24/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_latest/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7372/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7693/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8072/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8689/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8586/
install -d %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8732/
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2_24 M=%{_builddir}/neuron_2_24 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_latest M=%{_builddir}/neuron_latest modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_7372 M=%{_builddir}/neuron_2x_7372 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_7693 M=%{_builddir}/neuron_2x_7693 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_8072 M=%{_builddir}/neuron_2x_8072 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_8689 M=%{_builddir}/neuron_2x_8689 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_8586 M=%{_builddir}/neuron_2x_8586 modules_install
%kmake -C %{kernel_sources} %{?_smp_mflags} KERNELRELEASE=%{kmajor} DEPMOD=true INSTALL_MOD_DIR=neuron_2x_8732 M=%{_builddir}/neuron_2x_8732 modules_install
mv %{buildroot}%{_cross_kmoddir}/neuron_2_24/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2_24/
mv %{buildroot}%{_cross_kmoddir}/neuron_latest/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_latest/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_7372/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7372/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_7693/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_7693/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_8072/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8072/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_8689/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8689/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_8586/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8586/
mv %{buildroot}%{_cross_kmoddir}/neuron_2x_8732/neuron.%{_ko} %{buildroot}%{_cross_libexecdir}/neuron/neuron_2x_8732/

# Add Neuron-related configuration files to load the module when the hardware is present.
install -d 0644 %{buildroot}%{_cross_tmpfilesdir}
sed \
  -e "s|__KERNEL_VERSION__|%{kmajor}|" \
  -e "s|__PREFIX__|%{_cross_prefix}|" %{S:220} > neuron.conf
install -p -m 0644 neuron.conf %{buildroot}%{_cross_tmpfilesdir}/
install -d 0644 %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
# inf1
sed -e 's|__NEURON_MODULES__|%{_cross_libexecdir}/neuron|' %{S:221} > \
  neuron-inf1.toml
install -m 0644 neuron-inf1.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
# latest
sed -e 's|__NEURON_MODULES__|%{_cross_libexecdir}/neuron|' %{S:223} > \
  neuron-latest.toml
install -m 0644 neuron-latest.toml %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/drivers
install -d %{buildroot}%{_cross_unitdir}
install -p -m 0644 %{S:222} %{S:224} %{buildroot}%{_cross_unitdir}

%files
%{_cross_attribution_file}
%{_cross_tmpfilesdir}/neuron.conf

%files latest
%{_cross_libexecdir}/neuron/neuron_latest/neuron.%{_ko}
%{_cross_unitdir}/load-neuron-latest-modules.service
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/neuron-latest.toml

%files inf1
%{_cross_libexecdir}/neuron/neuron_2_24/neuron.%{_ko}
%{_cross_unitdir}/load-neuron-inf1-modules.service
%{_cross_factorydir}%{_cross_sysconfdir}/drivers/neuron-inf1.toml

%files extras
%{_cross_libexecdir}/neuron/neuron_2x_7372/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_7693/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_8072/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_8586/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_8689/neuron.%{_ko}
%{_cross_libexecdir}/neuron/neuron_2x_8732/neuron.%{_ko}

%changelog
