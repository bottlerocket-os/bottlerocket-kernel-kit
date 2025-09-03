%global debug_package %{nil}
%global __strip /bin/true

%global kmajor 6.12

Name: %{_cross_os}kernel-%{kmajor}
Version: 6.12.40
Release: 1%{?dist}
Summary: The Linux kernel
License: GPL-2.0 WITH Linux-syscall-note
URL: https://www.kernel.org/
# Use latest-kernel-srpm-url.sh to get this.
Source0: https://cdn.amazonlinux.com/al2023/blobstore/8d0c6b5bec3d237426610b35ee6d90b147f09becd3a62304794c67a471e250e3/kernel6.12-6.12.40-63.114.amzn2023.src.rpm
Source1: gpgkey-B21C50FA44A99720EAA72F7FE951904AD832C631.asc
# Use latest-neuron-srpm-url.sh to get this.
Source2: https://yum.repos.neuron.amazonaws.com/aws-neuronx-dkms-2.21.37.0.noarch.rpm
Source3: gpgkey-00FA2C1079260870A76D2C285749CAD8646D9185.asc

Source100: config-bottlerocket
Source101: config-full-bottlerocket-x86_64
Source102: config-full-bottlerocket-aarch64

# This list of FIPS modules is extracted from /etc/fipsmodules in the initramfs
# after placing AL2023 in FIPS mode.
Source200: check-fips-modules.drop-in.conf.in
Source201: fipsmodules-x86_64
Source202: fipsmodules-aarch64

# Adjust kernel-devel mount behavior if not squashfs.
Source210: var-lib-kernel-devel-lower.mount.drop-in.conf.in

# Neuron-related drop-ins.
Source220: neuron-sysinit.target.drop-in.conf
Source221: modprobe@neuron.service.drop-in.conf

# Bootconfig snippets to adjust the default kernel command line for the platform.
Source300: bootconfig-aws.conf
Source301: bootconfig-vmware.conf

# Help out-of-tree module builds run `make prepare` automatically.
Patch1001: 1001-Makefile-add-prepare-target-for-external-modules.patch
# Expose tools/* targets for out-of-tree module builds.
Patch1002: 1002-Revert-kbuild-hide-tools-build-targets-from-external.patch
# Enable INITRAMFS_FORCE config option for our use case.
Patch1003: 1003-initramfs-unlink-INITRAMFS_FORCE-from-CMDLINE_-EXTEN.patch
# Increase default of sysctl net.unix.max_dgram_qlen to 512.
Patch1004: 1004-af_unix-increase-default-max_dgram_qlen-to-512.patch
# Silence compiler error in Lustre sources
Patch1005: 1005-Lustre-cast-unsigned-long-to-pointer.patch
# Select prerequisites for GPU drivers
Patch1006: 1006-Select-prerequisites-for-gpu-drivers.patch
# Backport patch to ensure NUL-terminated task->comm buffer
Patch1007: 1007-strscpy-write-destination-buffer-only-once.patch

BuildRequires: bc
BuildRequires: elfutils-devel
BuildRequires: hostname
BuildRequires: kmod
BuildRequires: openssl-devel

# CPU microcode updates are included as "extra firmware" so the files don't
# need to be installed on the root filesystem. However, we want the license and
# attribution files to be available in the usual place.
%if "%{_cross_arch}" == "x86_64"
BuildRequires: %{_cross_os}microcode-ec2
Requires: %{_cross_os}microcode-licenses
%endif

# No bare-metal for this kernel
Conflicts: %{_cross_os}variant-platform(metal)

# No squashfs support, rely on erofs for compression
Conflicts: %{_cross_os}image-feature(no-erofs-root-partition)

# No runtime kernel-devel support
Conflicts: %{_cross_os}image-feature(external-kmod-development)

# Pull in expected modules.
Requires: %{name}-modules = %{version}-%{release}

# Pull in default mkfs conf for xfsprogs.
Requires: (%{name}-mkfs-xfs-conf if %{_cross_os}xfsprogs)

# Pull in platform-dependent boot config snippets.
Requires: (%{name}-bootconfig-aws if %{_cross_os}variant-platform(aws))
Requires: (%{name}-bootconfig-vmware if %{_cross_os}variant-platform(vmware))

# Pull in platform-dependent modules.
%if "%{_cross_arch}" == "x86_64"
Requires: (%{name}-modules-neuron if (%{_cross_os}variant-platform(aws) without %{_cross_os}variant-flavor(nvidia)))
%endif

# Pull in FIPS-related files if needed.
Requires: (%{name}-fips if %{_cross_os}image-feature(fips))

%global _cross_ksrcdir %{_cross_usrsrc}/kernels/%{version}
%global _cross_kmoddir %{_cross_libdir}/modules/%{version}

%description
%{summary}.

%package devel
Summary: Configured Linux kernel source for module building

%description devel
%{summary}.

%package bootconfig-aws
Summary: Boot config snippet for the Linux kernel on AWS

%description bootconfig-aws
%{summary}.

%package bootconfig-vmware
Summary: Boot config snippet for the Linux kernel on VMware

%description bootconfig-vmware
%{summary}.

%package modules
Summary: Modules for the Linux kernel

%description modules
%{summary}.

%package mkfs-xfs-conf
Summary: mkfs configurations for the XFS filesystem

%description mkfs-xfs-conf
%{summary}.

%if "%{_cross_arch}" == "x86_64"
%package modules-neuron
Summary: Modules for the Linux kernel with Neuron hardware
Requires: %{name}
Requires: %{_cross_os}ghostdog
Requires: %{_cross_os}variant-platform(aws)
Conflicts: %{_cross_os}variant-flavor(nvidia)

%description modules-neuron
%{summary}.
%endif

%package headers
Summary: Header files for the Linux kernel for use by glibc

%description headers
%{summary}.

%package fips
Summary: FIPS related configuration for the Linux kernel
Requires: (%{_cross_os}image-feature(fips) and %{name})
Conflicts: %{_cross_os}image-feature(no-fips)

%description fips
%{summary}.

%prep
%if "%{_cross_arch}" == "aarch64"
%global _cross_kimage vmlinuz.efi
%endif

%global _ko ko

rpmkeys --import %{S:1} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:0} --dbpath "${PWD}/rpmdb"
rm -rf "${PWD}/rpmdb"
rpm2cpio %{S:0} | cpio -iu {,./}linux-%{version}.tar.xz {,./}config-%{_cross_arch} {,./}"*.patch" {,./}kernel6.12.spec
tar -xof linux-%{version}.tar.xz; rm linux-%{version}.tar.xz
# Count all the patches extracted from the SRPM
patches_count=$(find -name "*.patch" | wc -l)
# Find patch ordering based on the Source0 kernel.spec file from the SRPM.
# First, find all `PatchNNN` lines. Then, sort by the patch number (-k1.6 in sort sets the 6th char
# in field 1 of input as the sort parameter). Finally, capture just the patch file name specified.
readarray -t patches < <(grep -P "^Patch\d+" kernel6.12.spec | sort -n -k1.6 | grep -oP "^Patch\d+: \K.*\.patch$" kernel6.12.spec)
# Fail the build if there is a mismatch in the number of patches found
if [[ "${patches_count}" -ne "${#patches[@]}" ]]; then
  echo "Mismatch on patches count!"
  exit 1
fi

%setup -TDn linux-%{version}
# Patches from the Source0 SRPM
for patch in ${patches[@]}; do
    patch -p1 <../"$patch"
done
# Patches listed in this spec (Patch0001...)
%autopatch -p1

%if "%{_cross_arch}" == "x86_64"
microcode="$(find %{_cross_libdir}/firmware -type f -path '*/*-ucode/*' -printf '%%P\n' | sort | tr '\n' ' ')"
cat <<EOF > ../config-microcode
CONFIG_EXTRA_FIRMWARE="${microcode}"
CONFIG_EXTRA_FIRMWARE_DIR="%{_cross_libdir}/firmware"
EOF
%endif

export ARCH="%{_cross_karch}"
export CROSS_COMPILE="%{_cross_target}-"

export KCONFIG_CONFIG="arch/%{_cross_karch}/configs/%{_cross_vendor}_defconfig"
scripts/kconfig/merge_config.sh \
  ../config-%{_cross_arch} \
%if "%{_cross_arch}" == "x86_64"
  ../config-microcode \
%endif
  %{S:100}

%if "%{_cross_arch}" == "x86_64"
SOURCE_FILE="%{S:101}"
%else
SOURCE_FILE="%{S:102}"
%endif
if ! diff "${KCONFIG_CONFIG}" "${SOURCE_FILE}"; then
  echo "error: source and build kernel configurations do not match"
  exit 1
fi

rm -f ../config-* ../*.patch

%if "%{_cross_arch}" == "x86_64"
cd %{_builddir}
rpmkeys --import %{S:3} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:2} --dbpath "${PWD}/rpmdb"
rm -rf "${PWD}/rpmdb"
rpm2cpio %{S:2} | cpio -idmu './usr/src/aws-neuronx-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} neuron \;
rm -r usr
%endif

%global kmake \
make -s\\\
  ARCH="%{_cross_karch}"\\\
  CROSS_COMPILE="%{_cross_target}-"\\\
  INSTALL_HDR_PATH="%{buildroot}%{_cross_prefix}"\\\
  INSTALL_MOD_PATH="%{buildroot}%{_cross_prefix}"\\\
  INSTALL_MOD_STRIP=1\\\
%{nil}

%build
%kmake mrproper
%kmake %{_cross_vendor}_defconfig
%kmake %{?_smp_mflags} %{_cross_kimage}
%kmake %{?_smp_mflags} modules

%if "%{_cross_arch}" == "x86_64"
%kmake %{?_smp_mflags} M=%{_builddir}/neuron
%endif

make -C tools/bpf/bpftool bootstrap
./tools/bpf/bpftool/bootstrap/bpftool btf dump file vmlinux format c > vmlinux.h

%install
%kmake %{?_smp_mflags} headers_install
%kmake %{?_smp_mflags} modules_install

%if "%{_cross_arch}" == "x86_64"
%kmake %{?_smp_mflags} M=%{_builddir}/neuron modules_install
%endif

install -d %{buildroot}/boot
install -T -m 0755 arch/%{_cross_karch}/boot/%{_cross_kimage} %{buildroot}/boot/vmlinuz
install -m 0644 .config %{buildroot}/boot/config

find %{buildroot}%{_cross_prefix} \
   \( -name .install -o -name .check -o \
      -name ..install.cmd -o -name ..check.cmd \) -delete

# For out-of-tree kmod builds, we need to support the following targets:
#   make scripts -> make prepare -> make modules
#
# This requires enough of the kernel tree to build host programs under the
# "scripts" and "tools" directories.

# Any existing ELF objects will not work properly if we're cross-compiling for
# a different architecture, so get rid of them to avoid confusing errors.
find arch scripts tools -type f -executable \
  -exec sh -c "head -c4 {} | grep -q ELF && rm {}" \;

# We don't need to include these files.
find -type f \( -name \*.cmd -o -name \*.gitignore \) -delete

# Avoid an OpenSSL dependency by stubbing out options for module signing and
# trusted keyrings, so `sign-file` and `extract-cert` won't be built. External
# kernel modules do not have access to the keys they would need to make use of
# these tools.
sed -i \
  -e 's,$(CONFIG_MODULE_SIG_FORMAT),n,g' \
  -e 's,$(CONFIG_SYSTEM_TRUSTED_KEYRING),n,g' \
  scripts/Makefile

(
  find * \
    -type f \
    \( -name Build\* -o -name Kbuild\* -o -name Kconfig\* -o -name Makefile\* \) \
    -print

  find arch/%{_cross_karch}/ \
    -type f \
    \( -name module.lds -o -name vmlinux.lds.S -o -name Platform -o -name \*.tbl \) \
    -print

  find arch/%{_cross_karch}/{include,lib}/ -type f ! -name \*.o ! -name \*.o.d ! -name \*.a -print
  echo arch/%{_cross_karch}/kernel/asm-offsets.s
  echo lib/vdso/gettimeofday.c

  for d in \
    arch/%{_cross_karch}/tools \
    arch/%{_cross_karch}/kernel/vdso ; do
    [ -d "${d}" ] && find "${d}/" -type f ! -name \*.o -print
  done

  find include -type f -print
  find scripts -type f ! -name \*.l ! -name \*.y ! -name \*.o -print

  find tools/{arch/%{_cross_karch},include,objtool,scripts}/ -type f ! -name \*.o ! -name \*.a -print
  echo tools/build/fixdep.c
  find tools/lib/subcmd -type f -print
  find tools/lib/{ctype,hweight,rbtree,string,str_error_r}.c

  echo kernel/bounds.c
  echo kernel/time/timeconst.bc
  echo security/selinux/include/classmap.h
  echo security/selinux/include/initial_sid_to_string.h
  echo security/selinux/include/policycap.h
  echo security/selinux/include/policycap_names.h

  echo .config
  echo Module.symvers
  echo System.map
  echo vmlinux.h
) | sort -u > kernel_devel_files

# Install development files into the canonical location for use by downstream
# packages as a build dependency.
install -d %{buildroot}%{_cross_ksrcdir}
tar c -T kernel_devel_files | tar x -C %{buildroot}%{_cross_ksrcdir}

# Replace the incorrect links from modules_install.
rm -f %{buildroot}%{_cross_kmoddir}/build %{buildroot}%{_cross_kmoddir}/source
ln -rs %{_cross_ksrcdir} %{buildroot}%{_cross_kmoddir}/build
ln -rs %{_cross_ksrcdir} %{buildroot}%{_cross_kmoddir}/source

# Make it easy to find sources and modules across minor version changes.
ln -rs %{buildroot}%{_cross_ksrcdir} %{buildroot}%{_cross_usrsrc}/kernels/%{kmajor}
ln -rs %{buildroot}%{_cross_kmoddir} %{buildroot}%{_cross_libdir}/modules/%{kmajor}

# Install a copy of System.map so that module dependencies can be regenerated.
install -p -m 0600 System.map %{buildroot}%{_cross_kmoddir}

# Ensure that each required FIPS module is loaded as a dependency of the
# check-fips-module.service. The list of FIPS modules is different across
# kernels but the check is consistent: it loads the "tcrypt" module after
# the other modules are loaded.
mkdir -p %{buildroot}%{_cross_unitdir}/check-fips-modules.service.d
i=0
for fipsmod in $(cat %{_sourcedir}/fipsmodules-%{_cross_arch}) ; do
  [ "${fipsmod}" == "tcrypt" ] && continue
  drop_in="$(printf "%03d\n" "${i}")-${fipsmod}.conf"
  sed -e "s|__FIPS_MODULE__|${fipsmod}|g" %{S:200} \
    > %{buildroot}%{_cross_unitdir}/check-fips-modules.service.d/"${drop_in}"
  (( i+=1 ))
done

# Create the mount point for the runtime kernel-devel directory, and populate
# with the linker script that driverdog needs.
install -d %{buildroot}%{_cross_datadir}/bottlerocket/kernel-devel/%{version}/scripts
install -p -m 0644 scripts/module.lds \
  %{buildroot}%{_cross_datadir}/bottlerocket/kernel-devel/%{version}/scripts

# Add a drop-in for compatibility with the release package's mount unit.
LOWERPATH=$(systemd-escape --path %{_cross_sharedstatedir}/kernel-devel/.overlay/lower)
mkdir -p %{buildroot}%{_cross_unitdir}/"${LOWERPATH}.mount.d"
sed -e 's|PREFIX|%{_cross_prefix}|g' %{S:210} \
  > %{buildroot}%{_cross_unitdir}/"${LOWERPATH}.mount.d"/no-squashfs.conf

# Add symlink for kernel 6.12 xfsprogs-mkfs defaults in the default path.
mkdir -p %{buildroot}%{_cross_datadir}/xfsprogs/mkfs
ln -s lts_6.12.conf %{buildroot}%{_cross_datadir}/xfsprogs/mkfs/default.conf

%if "%{_cross_arch}" == "x86_64"
# Add Neuron-related drop-ins to load the module when the hardware is present.
mkdir -p %{buildroot}%{_cross_unitdir}/sysinit.target.d
install -p -m 0644 %{S:220} %{buildroot}%{_cross_unitdir}/sysinit.target.d/neuron.conf

mkdir -p %{buildroot}%{_cross_unitdir}/modprobe@neuron.service.d
install -p -m 0644 %{S:221} %{buildroot}%{_cross_unitdir}/modprobe@neuron.service.d/neuron.conf
%endif

# Install platform-specific bootconfig snippets.
install -d %{buildroot}%{_cross_bootconfigdir}
install -p -m 0644 %{S:300} %{buildroot}%{_cross_bootconfigdir}/05-aws.conf
install -p -m 0644 %{S:301} %{buildroot}%{_cross_bootconfigdir}/05-vmware.conf

%files
%license COPYING LICENSES/preferred/GPL-2.0 LICENSES/exceptions/Linux-syscall-note
%{_cross_attribution_file}
/boot/vmlinuz
/boot/config
%dir %{_cross_usrsrc}/kernels
%dir %{_cross_datadir}/bottlerocket/kernel-devel
%{_cross_datadir}/bottlerocket/kernel-devel/*
%{_cross_unitdir}/*kernel*devel*.mount.d/no-squashfs.conf

%files mkfs-xfs-conf
%{_cross_datadir}/xfsprogs/mkfs/default.conf

%files headers
%dir %{_cross_includedir}/asm
%dir %{_cross_includedir}/asm-generic
%dir %{_cross_includedir}/drm
%dir %{_cross_includedir}/linux
%dir %{_cross_includedir}/misc
%dir %{_cross_includedir}/mtd
%dir %{_cross_includedir}/rdma
%dir %{_cross_includedir}/regulator
%dir %{_cross_includedir}/scsi
%dir %{_cross_includedir}/sound
%dir %{_cross_includedir}/video
%dir %{_cross_includedir}/xen
%{_cross_includedir}/asm/*
%{_cross_includedir}/asm-generic/*
%{_cross_includedir}/drm/*
%{_cross_includedir}/linux/*
%{_cross_includedir}/misc/*
%{_cross_includedir}/mtd/*
%{_cross_includedir}/rdma/*
%{_cross_includedir}/regulator/*
%{_cross_includedir}/scsi/*
%{_cross_includedir}/sound/*
%{_cross_includedir}/video/*
%{_cross_includedir}/xen/*

%files devel
# Allow downstream package builds to modify these files, since they need to
# rebuild tools for the current host architecture.
%defattr(664, root, builder, 775)
%{_cross_usrsrc}/kernels/%{kmajor}
%{_cross_ksrcdir}
%{_cross_kmoddir}/source
%{_cross_kmoddir}/build

%files fips
%{_cross_unitdir}/check-fips-modules.service.d/*.conf

%files bootconfig-aws
%{_cross_bootconfigdir}/05-aws.conf

%files bootconfig-vmware
%{_cross_bootconfigdir}/05-vmware.conf

%files modules
%dir %{_cross_libdir}/modules
%{_cross_libdir}/modules/%{kmajor}
%dir %{_cross_kmoddir}
%{_cross_kmoddir}/modules.alias
%{_cross_kmoddir}/modules.alias.bin
%{_cross_kmoddir}/modules.builtin
%{_cross_kmoddir}/modules.builtin.alias.bin
%{_cross_kmoddir}/modules.builtin.bin
%{_cross_kmoddir}/modules.builtin.modinfo
%{_cross_kmoddir}/modules.dep
%{_cross_kmoddir}/modules.dep.bin
%{_cross_kmoddir}/modules.devname
%{_cross_kmoddir}/modules.order
%{_cross_kmoddir}/modules.softdep
%{_cross_kmoddir}/modules.symbols
%{_cross_kmoddir}/modules.symbols.bin
%{_cross_kmoddir}/modules.weakdep
%{_cross_kmoddir}/System.map

%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/arch/x86/crypto/blowfish-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/camellia-aesni-avx2.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/camellia-aesni-avx-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/camellia-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/cast5-avx-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/cast6-avx-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/chacha-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/crc32c-intel.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/crc32-pclmul.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/curve25519-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/des3_ede-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/ghash-clmulni-intel.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/poly1305-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/serpent-avx2.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/serpent-avx-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/serpent-sse2-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/twofish-avx-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/twofish-x86_64-3way.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/crypto/twofish-x86_64.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/kvm/kvm-amd.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/kvm/kvm-intel.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/kvm/kvm.%{_ko}
%{_cross_kmoddir}/kernel/arch/x86/platform/intel/iosf_mbi.%{_ko}
%endif
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/arch/arm64/crypto/aes-arm64.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/aes-ce-blk.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/aes-ce-ccm.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/aes-ce-cipher.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/aes-neon-blk.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/aes-neon-bs.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/chacha-neon.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/ghash-ce.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/poly1305-neon.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/sha1-ce.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/sha3-ce.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/sm3-ce.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/crypto/sm4-ce-cipher.%{_ko}
%{_cross_kmoddir}/kernel/arch/arm64/lib/xor-neon.%{_ko}
%endif
%{_cross_kmoddir}/kernel/crypto/af_alg.%{_ko}
%{_cross_kmoddir}/kernel/crypto/algif_aead.%{_ko}
%{_cross_kmoddir}/kernel/crypto/algif_hash.%{_ko}
%{_cross_kmoddir}/kernel/crypto/algif_rng.%{_ko}
%{_cross_kmoddir}/kernel/crypto/algif_skcipher.%{_ko}
%{_cross_kmoddir}/kernel/crypto/ansi_cprng.%{_ko}
%{_cross_kmoddir}/kernel/crypto/anubis.%{_ko}
%{_cross_kmoddir}/kernel/crypto/arc4.%{_ko}
%{_cross_kmoddir}/kernel/crypto/asymmetric_keys/pkcs7_test_key.%{_ko}
%{_cross_kmoddir}/kernel/crypto/asymmetric_keys/pkcs8_key_parser.%{_ko}
%{_cross_kmoddir}/kernel/crypto/async_tx/async_memcpy.%{_ko}
%{_cross_kmoddir}/kernel/crypto/async_tx/async_pq.%{_ko}
%{_cross_kmoddir}/kernel/crypto/async_tx/async_raid6_recov.%{_ko}
%{_cross_kmoddir}/kernel/crypto/async_tx/async_tx.%{_ko}
%{_cross_kmoddir}/kernel/crypto/async_tx/async_xor.%{_ko}
%{_cross_kmoddir}/kernel/crypto/authencesn.%{_ko}
%{_cross_kmoddir}/kernel/crypto/authenc.%{_ko}
%{_cross_kmoddir}/kernel/crypto/blake2b_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/blowfish_common.%{_ko}
%{_cross_kmoddir}/kernel/crypto/blowfish_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/camellia_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cast5_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cast6_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cast_common.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cbc.%{_ko}
%{_cross_kmoddir}/kernel/crypto/ccm.%{_ko}
%{_cross_kmoddir}/kernel/crypto/chacha20poly1305.%{_ko}
%{_cross_kmoddir}/kernel/crypto/chacha_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cmac.%{_ko}
%{_cross_kmoddir}/kernel/crypto/crc32_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/crypto_user.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cts.%{_ko}
%{_cross_kmoddir}/kernel/crypto/des_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/echainiv.%{_ko}
%{_cross_kmoddir}/kernel/crypto/essiv.%{_ko}
%{_cross_kmoddir}/kernel/crypto/fcrypt.%{_ko}
%{_cross_kmoddir}/kernel/crypto/gcm.%{_ko}
%{_cross_kmoddir}/kernel/crypto/keywrap.%{_ko}
%{_cross_kmoddir}/kernel/crypto/khazad.%{_ko}
%{_cross_kmoddir}/kernel/crypto/lrw.%{_ko}
%{_cross_kmoddir}/kernel/crypto/lz4hc.%{_ko}
%{_cross_kmoddir}/kernel/crypto/lz4.%{_ko}
%{_cross_kmoddir}/kernel/crypto/md4.%{_ko}
%{_cross_kmoddir}/kernel/crypto/michael_mic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/pcbc.%{_ko}
%{_cross_kmoddir}/kernel/crypto/pcrypt.%{_ko}
%{_cross_kmoddir}/kernel/crypto/poly1305_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/rmd160.%{_ko}
%{_cross_kmoddir}/kernel/crypto/seed.%{_ko}
%{_cross_kmoddir}/kernel/crypto/serpent_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/tcrypt.%{_ko}
%{_cross_kmoddir}/kernel/crypto/tea.%{_ko}
%{_cross_kmoddir}/kernel/crypto/twofish_common.%{_ko}
%{_cross_kmoddir}/kernel/crypto/twofish_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/vmac.%{_ko}
%{_cross_kmoddir}/kernel/crypto/wp512.%{_ko}
%{_cross_kmoddir}/kernel/crypto/xcbc.%{_ko}
%{_cross_kmoddir}/kernel/crypto/xor.%{_ko}
%{_cross_kmoddir}/kernel/crypto/xts.%{_ko}
%{_cross_kmoddir}/kernel/crypto/xxhash_generic.%{_ko}
%{_cross_kmoddir}/kernel/crypto/zstd.%{_ko}
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/crypto/sm3.%{_ko}
%{_cross_kmoddir}/kernel/crypto/sm4.%{_ko}
%{_cross_kmoddir}/kernel/crypto/cryptd.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/acpi/ac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/acpi/button.%{_ko}
%{_cross_kmoddir}/kernel/drivers/acpi/thermal.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/acpi/acpi_extlog.%{_ko}
%{_cross_kmoddir}/kernel/drivers/acpi/acpi_pad.%{_ko}
%{_cross_kmoddir}/kernel/drivers/acpi/video.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/amazon/media/v4l2-loopback/v4l2loopback.%{_ko}
%{_cross_kmoddir}/kernel/drivers/amazon/net/efa/efa.%{_ko}
%{_cross_kmoddir}/kernel/drivers/amazon/net/ena/ena.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/brd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/drbd/drbd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/loop.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/nbd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/null_blk/null_blk.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/rbd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/block/zram/zram.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/ipmi/ipmi_msghandler.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/virtio_console.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/char/hangcheck-timer.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/nvram.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/char/hw_random/rng-core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/hw_random/virtio-rng.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/char/hw_random/amd-rng.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/hw_random/intel-rng.%{_ko}
%endif
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/char/hw_random/arm_smccc_trng.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/hw_random/cn10k-rng.%{_ko}
%{_cross_kmoddir}/kernel/drivers/char/hw_random/graviton-rng.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/cpufreq/cpufreq_conservative.%{_ko}
%{_cross_kmoddir}/kernel/drivers/cpufreq/cpufreq_ondemand.%{_ko}
%{_cross_kmoddir}/kernel/drivers/cpufreq/cpufreq_powersave.%{_ko}
%{_cross_kmoddir}/kernel/drivers/cpufreq/cpufreq_userspace.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/cpufreq/acpi-cpufreq.%{_ko}
%{_cross_kmoddir}/kernel/drivers/cpufreq/pcc-cpufreq.%{_ko}
%{_cross_kmoddir}/kernel/drivers/dca/dca.%{_ko}
%{_cross_kmoddir}/kernel/drivers/dma/ioat/ioatdma.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/amd64_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/e752x_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i3000_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i3200_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i5100_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i5400_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i7300_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i7core_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/i82975x_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/ie31200_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/pnd2_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/sb_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/skx_edac.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/skx_edac_common.%{_ko}
%{_cross_kmoddir}/kernel/drivers/edac/x38_edac.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/firmware/dmi-sysfs.%{_ko}
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/firmware/arm_ffa/ffa-core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/firmware/arm_ffa/ffa-module.%{_ko}
%{_cross_kmoddir}/kernel/drivers/firmware/arm_scpi.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/gpu/drm/drm_kms_helper.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/drm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/drm_shmem_helper.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/drm_suballoc_helper.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/drm_ttm_helper.%{_ko}

%{_cross_kmoddir}/kernel/drivers/gpu/drm/tiny/simpledrm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/display/drm_display_helper.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/ttm/ttm.%{_ko}

%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/gpu/drm/vmwgfx/vmwgfx.%{_ko}
%endif

%{_cross_kmoddir}/kernel/drivers/hid/hid-generic.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hid/hid-multitouch.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hid/uhid.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hid/usbhid/usbhid.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/hid/hid-hyperv.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hv/hv_balloon.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hv/hv_utils.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hv/hv_vmbus.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/hwmon/acpi_power_meter.%{_ko}
%{_cross_kmoddir}/kernel/drivers/hwmon/hwmon.%{_ko}
%{_cross_kmoddir}/kernel/drivers/i2c/algos/i2c-algo-bit.%{_ko}
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/i2c/busses/i2c-tegra-bpmp.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/i2c/i2c-core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/ib_cm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/ib_core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/ib_umad.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/ib_uverbs.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/iw_cm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/rdma_cm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/core/rdma_ucm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/infiniband/hw/mlx5/mlx5_ib.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/input/keyboard/atkbd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/mouse/psmouse.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/input/misc/uinput.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/mousedev.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/input/serio/hyperv-keyboard.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/serio/i8042.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/serio/libps2.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/serio/serio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/serio/serport.%{_ko}
%{_cross_kmoddir}/kernel/drivers/input/vivaldi-fmap.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/input/sparse-keymap.%{_ko}
%{_cross_kmoddir}/kernel/drivers/iommu/virtio-iommu.%{_ko}
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/mailbox/arm_mhu_db.%{_ko}
%{_cross_kmoddir}/kernel/drivers/mailbox/arm_mhu.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/md/bcache/bcache.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-bio-prison.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-cache.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-cache-smq.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-crypt.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-delay.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-dust.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-flakey.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-integrity.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-log.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-log-userspace.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-log-writes.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-mirror.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-multipath.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-queue-length.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-raid.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-region-hash.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-round-robin.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-service-time.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-snapshot.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-thin-pool.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/dm-zero.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/linear.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/persistent-data/dm-persistent-data.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/raid0.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/raid10.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/raid1.%{_ko}
%{_cross_kmoddir}/kernel/drivers/md/raid456.%{_ko}
%{_cross_kmoddir}/kernel/drivers/media/mc/mc.%{_ko}
%{_cross_kmoddir}/kernel/drivers/media/v4l2-core/v4l2-dv-timings.%{_ko}
%{_cross_kmoddir}/kernel/drivers/media/v4l2-core/videodev.%{_ko}
%{_cross_kmoddir}/kernel/drivers/mfd/lpc_ich.%{_ko}
%{_cross_kmoddir}/kernel/drivers/mfd/lpc_sch.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/mfd/mfd-core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/misc/vmw_balloon.%{_ko}
%{_cross_kmoddir}/kernel/drivers/misc/vmw_vmci/vmw_vmci.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/misc/nsm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/bonding/bonding.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/dummy.%{_ko}

%{_cross_kmoddir}/kernel/drivers/net/ethernet/intel/e1000/e1000.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/intel/e1000e/e1000e.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/intel/igb/igb.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/intel/igc/igc.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/intel/ixgbevf/ixgbevf.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/mellanox/mlx5/core/mlx5_core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/mellanox/mlxfw/mlxfw.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ethernet/realtek/r8169.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/geneve.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/net/hyperv/hv_netvsc.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/net/ifb.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ipvlan/ipvlan.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/ipvlan/ipvtap.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/macvlan.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/macvtap.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/mdio/acpi_mdio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/mdio/fwnode_mdio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/netdevsim/netdevsim.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/net_failover.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/nlmon.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/phy/fixed_phy.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/phy/libphy.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/phy/mdio_devres.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/phy/realtek.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/tap.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/team/team.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/team/team_mode_activebackup.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/team/team_mode_broadcast.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/team/team_mode_loadbalance.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/team/team_mode_roundrobin.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/tun.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/veth.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/virtio_net.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/vmxnet3/vmxnet3.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/vrf.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/vxlan/vxlan.%{_ko}
%{_cross_kmoddir}/kernel/drivers/net/wireguard/wireguard.%{_ko}
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/net/mdio/of_mdio.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/nvme/host/nvme-fabrics.%{_ko}
%{_cross_kmoddir}/kernel/drivers/nvme/host/nvme-tcp.%{_ko}
%{_cross_kmoddir}/kernel/drivers/pci/hotplug/acpiphp_ibm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/pci/pci-stub.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/pci/controller/pci-hyperv-intf.%{_ko}
%{_cross_kmoddir}/kernel/drivers/pci/hotplug/cpcihp_generic.%{_ko}
%{_cross_kmoddir}/kernel/drivers/platform/x86/wmi-bmof.%{_ko}
%{_cross_kmoddir}/kernel/drivers/platform/x86/wmi.%{_ko}
%endif
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/perf/arm-cmn.%{_ko}
%{_cross_kmoddir}/kernel/drivers/pmdomain/arm/scpi_pm_domain.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/pps/clients/pps-gpio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/pps/clients/pps-ldisc.%{_ko}
%{_cross_kmoddir}/kernel/drivers/ptp/ptp_kvm.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/ras/amd/atl/amd_atl.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/scsi/raid_class.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/scsi_common.%{_ko}
%{_cross_kmoddir}/kernel/drivers/target/iscsi/iscsi_target_mod.%{_ko}
%{_cross_kmoddir}/kernel/drivers/target/target_core_file.%{_ko}
%{_cross_kmoddir}/kernel/drivers/target/target_core_iblock.%{_ko}
%{_cross_kmoddir}/kernel/drivers/target/target_core_mod.%{_ko}
%{_cross_kmoddir}/kernel/drivers/target/target_core_user.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/thermal/intel/x86_pkg_temp_thermal.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/tty/serial/8250/8250_exar.%{_ko}
%{_cross_kmoddir}/kernel/drivers/uio/uio_dmem_genirq.%{_ko}
%{_cross_kmoddir}/kernel/drivers/uio/uio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/uio/uio_pci_generic.%{_ko}
%{_cross_kmoddir}/kernel/drivers/uio/uio_pdrv_genirq.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/uio/uio_hv_generic.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/usb/class/cdc-acm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/common/usb-common.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/core/usbcore.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/ehci-hcd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/ehci-pci.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/ehci-platform.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/ohci-hcd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/ohci-pci.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/ohci-platform.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/uhci-hcd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/xhci-hcd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/xhci-pci.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/host/xhci-plat-hcd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/mon/usbmon.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/serial/cp210x.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/serial/ftdi_sio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/serial/usbserial.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/usbip/usbip-core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/usbip/usbip-host.%{_ko}
%{_cross_kmoddir}/kernel/drivers/usb/usbip/vhci-hcd.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vfio/pci/mlx5/mlx5-vfio-pci.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vfio/pci/vfio-pci-core.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vfio/pci/vfio-pci.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vfio/vfio_iommu_type1.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vfio/vfio.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vhost/vhost_iotlb.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vhost/vhost.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vhost/vhost_net.%{_ko}
%{_cross_kmoddir}/kernel/drivers/vhost/vhost_vsock.%{_ko}
%{_cross_kmoddir}/kernel/drivers/video/backlight/backlight.%{_ko}
%{_cross_kmoddir}/kernel/drivers/video/backlight/lcd.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/virt/coco/sev-guest/sev-guest.%{_ko}
%{_cross_kmoddir}/kernel/drivers/virt/coco/tsm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/virt/vboxguest/vboxguest.%{_ko}
%endif
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/virt/nitro_enclaves/nitro_enclaves.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/virtio/virtio_balloon.%{_ko}
%{_cross_kmoddir}/kernel/drivers/virtio/virtio_mmio.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/virtio/virtio_mem.%{_ko}
%endif
%{_cross_kmoddir}/kernel/drivers/watchdog/softdog.%{_ko}
%if "%{_cross_arch}" == "aarch64"
%{_cross_kmoddir}/kernel/drivers/watchdog/gpio_wdt.%{_ko}
%{_cross_kmoddir}/kernel/drivers/watchdog/sbsa_gwdt.%{_ko}
%{_cross_kmoddir}/kernel/drivers/watchdog/sp805_wdt.%{_ko}
%endif
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/xen/xen-evtchn.%{_ko}
%{_cross_kmoddir}/kernel/drivers/xen/xenfs/xenfs.%{_ko}
%{_cross_kmoddir}/kernel/drivers/xen/xen-gntalloc.%{_ko}
%{_cross_kmoddir}/kernel/drivers/xen/xen-gntdev.%{_ko}
%{_cross_kmoddir}/kernel/drivers/xen/xen-privcmd.%{_ko}
%endif

%{_cross_kmoddir}/kernel/drivers/scsi/scsi_transport_sas.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/iscsi_boot_sysfs.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/iscsi_tcp.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/libiscsi.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/libiscsi_tcp.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/scsi_mod.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/scsi_transport_iscsi.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/sd_mod.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/virtio_scsi.%{_ko}
%{_cross_kmoddir}/kernel/drivers/target/loopback/tcm_loop.%{_ko}

%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/drivers/scsi/hv_storvsc.%{_ko}
%{_cross_kmoddir}/kernel/drivers/scsi/vmw_pvscsi.%{_ko}
%endif

%{_cross_kmoddir}/kernel/fs/binfmt_misc.%{_ko}
%{_cross_kmoddir}/kernel/fs/cachefiles/cachefiles.%{_ko}
%{_cross_kmoddir}/kernel/fs/ceph/ceph.%{_ko}
%{_cross_kmoddir}/kernel/fs/configfs/configfs.%{_ko}
%{_cross_kmoddir}/kernel/fs/efivarfs/efivarfs.%{_ko}
%{_cross_kmoddir}/kernel/fs/exfat/exfat.%{_ko}
%{_cross_kmoddir}/kernel/fs/ext4/ext4.%{_ko}
%{_cross_kmoddir}/kernel/fs/fat/fat.%{_ko}
%{_cross_kmoddir}/kernel/fs/fat/msdos.%{_ko}
%{_cross_kmoddir}/kernel/fs/fat/vfat.%{_ko}
%{_cross_kmoddir}/kernel/fs/fuse/cuse.%{_ko}
%{_cross_kmoddir}/kernel/fs/fuse/fuse.%{_ko}
%{_cross_kmoddir}/kernel/fs/fuse/virtiofs.%{_ko}
%{_cross_kmoddir}/kernel/fs/isofs/isofs.%{_ko}
%{_cross_kmoddir}/kernel/fs/jbd2/jbd2.%{_ko}
%{_cross_kmoddir}/kernel/fs/lockd/lockd.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/fid/fid.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/fld/fld.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/llite/lustre.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/lmv/lmv.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/lov/lov.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/mdc/mdc.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/mgc/mgc.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/obdclass/obdclass.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/obdecho/obdecho.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/osc/osc.%{_ko}
%{_cross_kmoddir}/kernel/fs/lustre/ptlrpc/ptlrpc.%{_ko}
%{_cross_kmoddir}/kernel/fs/mbcache.%{_ko}
%{_cross_kmoddir}/kernel/fs/netfs/netfs.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs/blocklayout/blocklayoutdriver.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs_common/grace.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs_common/nfs_acl.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfsd/nfsd.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs/filelayout/nfs_layout_nfsv41_files.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs/flexfilelayout/nfs_layout_flexfiles.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs/nfs.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs/nfsv3.%{_ko}
%{_cross_kmoddir}/kernel/fs/nfs/nfsv4.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-celtic.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-centeuro.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-croatian.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-cyrillic.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-gaelic.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-greek.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-iceland.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-inuit.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-romanian.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-roman.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/mac-turkish.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_ascii.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp1250.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp1251.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp1255.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp437.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp737.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp775.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp850.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp852.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp855.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp857.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp860.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp861.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp862.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp863.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp864.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp865.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp866.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp869.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp874.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp932.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp936.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp949.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_cp950.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_euc-jp.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-13.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-14.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-15.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-1.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-2.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-3.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-4.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-5.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-6.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-7.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_iso8859-9.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_koi8-r.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_koi8-ru.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_koi8-u.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_ucs2_utils.%{_ko}
%{_cross_kmoddir}/kernel/fs/nls/nls_utf8.%{_ko}
%{_cross_kmoddir}/kernel/fs/overlayfs/overlay.%{_ko}
%{_cross_kmoddir}/kernel/fs/pstore/ramoops.%{_ko}
%{_cross_kmoddir}/kernel/fs/quota/quota_tree.%{_ko}
%{_cross_kmoddir}/kernel/fs/quota/quota_v2.%{_ko}
%{_cross_kmoddir}/kernel/fs/smb/client/cifs.%{_ko}
%{_cross_kmoddir}/kernel/fs/smb/common/cifs_arc4.%{_ko}
%{_cross_kmoddir}/kernel/fs/smb/common/cifs_md4.%{_ko}
%{_cross_kmoddir}/kernel/fs/udf/udf.%{_ko}
%{_cross_kmoddir}/kernel/kernel/bpf/preload/bpf_preload.%{_ko}
%{_cross_kmoddir}/kernel/kernel/kheaders.%{_ko}
%{_cross_kmoddir}/kernel/lib/asn1_encoder.%{_ko}
%{_cross_kmoddir}/kernel/lib/crc4.%{_ko}
%{_cross_kmoddir}/kernel/lib/crc7.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/lib/crc8.%{_ko}
%endif
%{_cross_kmoddir}/kernel/lib/crc16.%{_ko}
%{_cross_kmoddir}/kernel/lib/crc-itu-t.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libarc4.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libchacha20poly1305.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libchacha.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libcurve25519-generic.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libcurve25519.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libdes.%{_ko}
%{_cross_kmoddir}/kernel/lib/crypto/libpoly1305.%{_ko}
%{_cross_kmoddir}/kernel/lib/lru_cache.%{_ko}
%{_cross_kmoddir}/kernel/lib/lz4/lz4_compress.%{_ko}
%{_cross_kmoddir}/kernel/lib/lz4/lz4hc_compress.%{_ko}
%{_cross_kmoddir}/kernel/lib/raid6/raid6_pq.%{_ko}
%{_cross_kmoddir}/kernel/lib/reed_solomon/reed_solomon.%{_ko}
%{_cross_kmoddir}/kernel/lib/test_lockup.%{_ko}
%{_cross_kmoddir}/kernel/lib/ts_bm.%{_ko}
%{_cross_kmoddir}/kernel/lib/ts_fsm.%{_ko}
%{_cross_kmoddir}/kernel/lib/ts_kmp.%{_ko}
%{_cross_kmoddir}/kernel/lib/zstd/zstd_compress.%{_ko}
%{_cross_kmoddir}/kernel/mm/zsmalloc.%{_ko}
%{_cross_kmoddir}/kernel/net/8021q/8021q.%{_ko}
%{_cross_kmoddir}/kernel/net/802/garp.%{_ko}
%{_cross_kmoddir}/kernel/net/802/mrp.%{_ko}
%{_cross_kmoddir}/kernel/net/802/p8022.%{_ko}
%{_cross_kmoddir}/kernel/net/802/psnap.%{_ko}
%{_cross_kmoddir}/kernel/net/802/stp.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/bridge.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/br_netfilter.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_802_3.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebtable_broute.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebtable_filter.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebtable_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebtables.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_among.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_arp.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_arpreply.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_dnat.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_ip6.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_ip.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_limit.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_log.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_mark.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_mark_m.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_nflog.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_pkttype.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_redirect.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_snat.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_stp.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/ebt_vlan.%{_ko}
%{_cross_kmoddir}/kernel/net/bridge/netfilter/nft_reject_bridge.%{_ko}
%{_cross_kmoddir}/kernel/net/ceph/libceph.%{_ko}
%{_cross_kmoddir}/kernel/net/core/failover.%{_ko}
%{_cross_kmoddir}/kernel/net/core/selftests.%{_ko}
%{_cross_kmoddir}/kernel/net/dns_resolver/dns_resolver.%{_ko}
%{_cross_kmoddir}/kernel/net/ife/ife.%{_ko}
%{_cross_kmoddir}/kernel/net/mptcp/mptcp_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/sctp/sctp_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/ah4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/esp4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/esp4_offload.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/fou.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/gre.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/inet_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/ip_gre.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/ip_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/ip_vti.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/ipcomp.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/ipip.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/arp_tables.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/arpt_mangle.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/arptable_filter.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/ip_tables.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/ipt_ah.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/ipt_ECN.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/ipt_REJECT.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/ipt_rpfilter.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/ipt_SYNPROXY.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/iptable_filter.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/iptable_mangle.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/iptable_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/iptable_raw.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/iptable_security.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_defrag_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_dup_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_nat_h323.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_nat_pptp.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_nat_snmp_basic.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_reject_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_socket_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nf_tproxy_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nft_dup_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nft_fib_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/netfilter/nft_reject_ipv4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/raw_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_bbr.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_bic.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_dctcp.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_highspeed.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_htcp.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_hybla.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_illinois.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_lp.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_scalable.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_vegas.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_veno.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_westwood.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/udp_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tcp_yeah.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/tunnel4.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/udp_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv4/xfrm4_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ah6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/esp6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/esp6_offload.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/fou6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ila/ila.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ip6_gre.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ip6_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ip6_udp_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ip6_vti.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/ipcomp6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/mip6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6_tables.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_ah.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_eui64.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_frag.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_hbh.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_ipv6header.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_mh.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_REJECT.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_rpfilter.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_rt.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_srh.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6t_SYNPROXY.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6table_filter.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6table_mangle.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6table_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6table_raw.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/ip6table_security.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nf_defrag_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nf_dup_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nf_reject_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nf_socket_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nf_tproxy_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nft_dup_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nft_fib_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/netfilter/nft_reject_ipv6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/sit.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/tunnel6.%{_ko}
%{_cross_kmoddir}/kernel/net/ipv6/xfrm6_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/key/af_key.%{_ko}
%{_cross_kmoddir}/kernel/net/llc/llc.%{_ko}
%{_cross_kmoddir}/kernel/net/lnet/libcfs/libcfs/libcfs.%{_ko}
%{_cross_kmoddir}/kernel/net/lnet/lnet/klnds/efalnd/kefalnd.%{_ko}
%{_cross_kmoddir}/kernel/net/lnet/lnet/klnds/o2iblnd/ko2iblnd.%{_ko}
%{_cross_kmoddir}/kernel/net/lnet/lnet/klnds/socklnd/ksocklnd.%{_ko}
%{_cross_kmoddir}/kernel/net/lnet/lnet/lnet/lnet.%{_ko}
%{_cross_kmoddir}/kernel/net/lnet/lnet/selftest/lnet_selftest.%{_ko}
%{_cross_kmoddir}/kernel/net/mpls/mpls_gso.%{_ko}
%{_cross_kmoddir}/kernel/net/mpls/mpls_iptunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/mpls/mpls_router.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_bitmap_ip.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_bitmap_ipmac.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_bitmap_port.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_ip.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_ipmac.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_ipmark.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_ipportip.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_ipport.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_ipportnet.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_mac.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_netiface.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_net.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_netnet.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_netport.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_hash_netportnet.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipset/ip_set_list_set.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_dh.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_fo.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_ftp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_lblc.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_lblcr.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_lc.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_mh.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_nq.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_ovf.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_pe_sip.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_rr.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_sed.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_sh.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_wlc.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/ipvs/ip_vs_wrr.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conncount.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_amanda.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_broadcast.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_ftp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_h323.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_irc.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_netbios_ns.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_netlink.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_pptp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_sane.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_sip.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_snmp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_conntrack_tftp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_dup_netdev.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_flow_table_inet.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_flow_table.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_log_syslog.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_nat_amanda.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_nat_ftp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_nat_irc.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_nat_sip.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_nat_tftp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink_acct.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink_cthelper.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink_cttimeout.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink_log.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink_osf.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nfnetlink_queue.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_synproxy_core.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nf_tables.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_chain_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_compat.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_connlimit.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_ct.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_dup_netdev.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_fib_inet.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_fib.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_fib_netdev.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_flow_offload.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_fwd_netdev.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_hash.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_limit.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_log.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_masq.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_numgen.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_osf.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_queue.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_quota.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_redir.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_reject_inet.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_reject.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_socket.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_synproxy.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_tproxy.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_tunnel.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/nft_xfrm.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_addrtype.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_AUDIT.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_bpf.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_cgroup.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_CHECKSUM.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_CLASSIFY.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_cluster.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_comment.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_connbytes.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_connlabel.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_connlimit.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_connmark.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_CONNSECMARK.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_conntrack.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_cpu.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_CT.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_devgroup.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_dscp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_DSCP.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_ecn.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_esp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_hashlimit.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_helper.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_hl.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_HL.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_HMARK.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_IDLETIMER.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_ipcomp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_iprange.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_ipvs.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_l2tp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_length.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_limit.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_LOG.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_mac.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_mark.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_MASQUERADE.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_multiport.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_NETMAP.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_nfacct.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_NFLOG.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_NFQUEUE.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_osf.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_owner.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_physdev.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_pkttype.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_policy.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_quota.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_rateest.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_RATEEST.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_realm.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_recent.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_REDIRECT.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_sctp.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_SECMARK.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_set.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_socket.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_state.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_statistic.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_string.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_tcpmss.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_TCPMSS.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_TCPOPTSTRIP.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_TEE.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_time.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_TPROXY.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_TRACE.%{_ko}
%{_cross_kmoddir}/kernel/net/netfilter/xt_u32.%{_ko}
%{_cross_kmoddir}/kernel/net/netlink/netlink_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/nsh/nsh.%{_ko}
%{_cross_kmoddir}/kernel/net/openvswitch/openvswitch.%{_ko}
%{_cross_kmoddir}/kernel/net/openvswitch/vport-geneve.%{_ko}
%{_cross_kmoddir}/kernel/net/openvswitch/vport-gre.%{_ko}
%{_cross_kmoddir}/kernel/net/openvswitch/vport-vxlan.%{_ko}
%{_cross_kmoddir}/kernel/net/packet/af_packet_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/psample/psample.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_bpf.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_connmark.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_csum.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_gact.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_mirred.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_nat.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_pedit.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_police.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_sample.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_simple.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_skbedit.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/act_vlan.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_basic.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_bpf.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_cgroup.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_flow.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_flower.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_fw.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_route.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/cls_u32.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_cmp.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_ipset.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_ipt.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_meta.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_nbyte.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_text.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/em_u32.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_cbs.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_choke.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_codel.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_drr.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_fq_codel.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_fq.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_gred.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_hfsc.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_hhf.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_htb.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_ingress.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_mqprio_lib.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_mqprio.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_multiq.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_netem.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_pie.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_plug.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_prio.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_qfq.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_red.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_sfb.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_sfq.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_tbf.%{_ko}
%{_cross_kmoddir}/kernel/net/sched/sch_teql.%{_ko}
%{_cross_kmoddir}/kernel/net/sctp/sctp.%{_ko}
%{_cross_kmoddir}/kernel/net/sunrpc/auth_gss/auth_rpcgss.%{_ko}
%{_cross_kmoddir}/kernel/net/sunrpc/auth_gss/rpcsec_gss_krb5.%{_ko}
%{_cross_kmoddir}/kernel/net/sunrpc/sunrpc.%{_ko}
%{_cross_kmoddir}/kernel/net/tls/tls.%{_ko}
%{_cross_kmoddir}/kernel/net/unix/unix_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/vmw_vsock/vmw_vsock_virtio_transport_common.%{_ko}
%{_cross_kmoddir}/kernel/net/vmw_vsock/vmw_vsock_virtio_transport.%{_ko}
%{_cross_kmoddir}/kernel/net/vmw_vsock/vsock_diag.%{_ko}
%{_cross_kmoddir}/kernel/net/vmw_vsock/vsock.%{_ko}
%{_cross_kmoddir}/kernel/net/vmw_vsock/vsock_loopback.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/net/vmw_vsock/hv_sock.%{_ko}
%{_cross_kmoddir}/kernel/net/vmw_vsock/vmw_vsock_vmci_transport.%{_ko}
%endif
%{_cross_kmoddir}/kernel/net/xfrm/xfrm_algo.%{_ko}
%{_cross_kmoddir}/kernel/net/xfrm/xfrm_interface.%{_ko}
%{_cross_kmoddir}/kernel/net/xfrm/xfrm_ipcomp.%{_ko}
%{_cross_kmoddir}/kernel/net/xfrm/xfrm_user.%{_ko}
%{_cross_kmoddir}/kernel/security/keys/encrypted-keys/encrypted-keys.%{_ko}
%{_cross_kmoddir}/kernel/security/keys/trusted-keys/trusted.%{_ko}
%if "%{_cross_arch}" == "x86_64"
%{_cross_kmoddir}/kernel/virt/lib/irqbypass.ko
%endif

%if "%{_cross_arch}" == "x86_64"
%files modules-neuron
%{_cross_kmoddir}/updates/neuron.%{_ko}
%{_cross_unitdir}/sysinit.target.d/neuron.conf
%{_cross_unitdir}/modprobe@neuron.service.d/neuron.conf
%endif

%changelog
