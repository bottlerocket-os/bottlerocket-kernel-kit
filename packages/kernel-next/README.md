# kernel-next

This package contains the Bottlerocket Linux kernel built from the Amazon Linux 2027 `kernel7.2` SRPM.
This kernel is not an LTS kernel. Stability for this kernel is not guaranteed.
The `-next` in the package name means that the package follows upstream minor updates, for example from 7.2 to 7.3.

This kernel has no FIPS certification yet, so a FIPS variant cannot use it.

## Page size

On aarch64, this kernel uses 64K pages and uses the upstream's `config-aarch64-64k` kernel config.
The SRPM also has the 4K page `config-aarch64` which is unused.
On x86_64, this kernel uses 4K pages, from `config-x86_64`.

### Hugepage sizes on aarch64

This kernel uses 64K pages on aarch64, so the supported hugepage sizes are 2M, 512M, and 16G. The default hugepage size is 512M.
Setting `settings.kernel.hugepages.static."1Gi"` on aarch64 will result in a failed boot with `Unsupported huge page size 1048576 kiB`.

## Configuration Structure

During the build process, these configurations are merged in the following order:
1. Amazon Linux config from the SRPM (`../config-aarch64-64k` or `../config-x86_64`)
2. On x86_64, the microcode config that the build generates from `microcode-ec2`
3. Architecture-specific Bottlerocket config (`config-bottlerocket-aarch64` or `config-bottlerocket-x86_64`)
4. Common Bottlerocket config (`config-bottlerocket`)

The final merged configurations are written to:
* [`config-full-bottlerocket-aarch64-on-aarch64`](config-full-bottlerocket-aarch64-on-aarch64) - Complete ARM64 configuration for an ARM64 host
* [`config-full-bottlerocket-aarch64-on-x86_64`](config-full-bottlerocket-aarch64-on-x86_64) - Complete ARM64 configuration for an X86_64 host
* [`config-full-bottlerocket-x86_64-on-aarch64`](config-full-bottlerocket-x86_64-on-aarch64) - Complete X86_64 configuration for an ARM64 host
* [`config-full-bottlerocket-x86_64-on-x86_64`](config-full-bottlerocket-x86_64-on-x86_64) - Complete X86_64 configuration for an X86_64 host

## Testing of Configuration Changes

Bottlerocket kernels are built in multiple flavors (e.g. cloud, bare metal) and for multiple architectures (e.g. aarch64, x86_64).
The kernel configuration for any of those combinations might change independently of the others.
Please use [`tools/latest-kernel-full-config.sh`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/tree/develop/tools/latest-kernel-full-config.sh)
script from the this repository to ensure the configuration for any of the combinations does not change inadvertently:

```
# From the top-level bottlerocket-kernel-kit directory:
$ make full-config
```

Any resulting diff to the following:
- [`config-full-bottlerocket-aarch64-on-aarch64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-next/config-full-bottlerocket-aarch64-on-aarch64)
- [`config-full-bottlerocket-x86_64-on-aarch64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-next/config-full-bottlerocket-x86_64-on-aarch64)
- [`config-full-bottlerocket-aarch64-on-x86_64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-next/config-full-bottlerocket-aarch64-on-x86_64)
- [`config-full-bottlerocket-x86_64-on-x86_64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-next/config-full-bottlerocket-x86_64-on-x86_64)

should be PR'd to this package for review.

Changes that can have an effect on the resulting kernel configuration include:

* explicit kernel configuration changes in any of the source config files
* package updates/kernel rebases

## Module signing

The kernel opts in to kit module signing (`module-signing = true` in
`Cargo.toml`), so its modules are signed with the kit module-signing key.

`kernel-next-module-integrity`, which the kernel pulls in for UKI images,
provides a boot config snippet that enforces module signatures and integrity
lockdown, blacklists the `binfmt_misc`, `efivarfs` and `i8042` modules, and
disables kexec loading.
