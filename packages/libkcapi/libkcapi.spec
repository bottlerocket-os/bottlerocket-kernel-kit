# Helper functions that use OpenSSL to compute an HMAC with specified keys.
%global openssl_sha512_hmac openssl sha512 -hmac FIPS-FTW-RHT2009 -hex
%global openssl_sha256_hmac openssl sha256 -hmac orboDeJITITejsirpADONivirpUkvarP -hex

# We need to compute the HMAC after the binaries have been stripped.
%define __spec_install_post\
%{?__debug_package:%{__debug_install_post}}\
%{__arch_install_post}\
%{__os_install_post}\
cd %{buildroot}/%{_cross_bindir}\
%openssl_sha512_hmac sha512hmac\\\
  | awk '{ print $2 }' > .sha512hmac.hmac\
cd %{buildroot}/%{_cross_libdir}\
%openssl_sha256_hmac libkcapi.so.%{version}\\\
  | awk '{ print $2 }' > .libkcapi.so.%{version}.hmac\
ln -s .libkcapi.so.%{version}.hmac .libkcapi.so.1.hmac\
%{nil}

Name: %{_cross_os}libkcapi
Version: 1.4.0
Release: 1%{?dist}
Epoch: 2
Summary: Library for kernel crypto API
License: BSD-3-Clause OR GPL-2.0-only
URL: https://www.chronox.de/libkcapi/html/index.html
Source0: https://cdn.amazonlinux.com/al2023/blobstore/0eef74b3b4eb1ec321bab80f867aee89b94dc9fc95571da58ea5bba7a70e6224/libkcapi-1.4.0-105.amzn2023.0.1.src.rpm
Source1: gpgkey-B21C50FA44A99720EAA72F7FE951904AD832C631.asc

%description
%{summary}.

%package devel
Summary: Files for development using the library for kernel crypto API
Requires: %{name}

%description devel
%{summary}.

%prep
rpmkeys --import %{S:1} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:0} --dbpath "${PWD}/rpmdb"
rm -rf "${PWD}/rpmdb"
rpm2cpio %{S:0} | cpio -iu libkcapi-%{version}.tar.xz
tar -xof libkcapi-%{version}.tar.xz; rm libkcapi-%{version}.tar.xz
%setup -TDn libkcapi-%{version}

%build
autoreconf -fi
%cross_configure \
  --disable-static \
  --enable-shared \
  --enable-kcapi-hasher \

%force_disable_rpath

%make_build

%install
%make_install

# Remove all binaries except `sha512hmac`.
find %{buildroot}%{_cross_bindir} -type f ! -name 'sha512hmac' -delete

# Clean up HMAC signatures, which will be regenerated.
find %{buildroot} -type f -name '*.hmac' -delete

%files
%license COPYING COPYING.bsd COPYING.gplv2
%{_cross_attribution_file}
%{_cross_libdir}/*.so.*
%{_cross_libdir}/.*.so.*.hmac
%{_cross_bindir}/sha512hmac
%{_cross_bindir}/.sha512hmac.hmac

%files devel
%{_cross_libdir}/*.so
%{_cross_includedir}/kcapi.h
%{_cross_pkgconfigdir}/*.pc

%changelog
