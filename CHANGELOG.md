# 3.2.1. (2025-07-24)

## OS Changes
 * Update r570 NVIDIA driver to 570.172.08
 * Update r535 NVIDIA driver to 535.261.03

# v3.2.0 (2025-07-16)

## Build Changes
* Update the Bottlerocket SDK to v0.63.0 ([#211])

[#211]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/211

# v3.1.2 (2025-07-10)

 ## OS Changes
 * Update kernels from 5.15.185 to 5.15.186 ([#208])
 * Update kernels from 6.1.141-155.222 to kernel-6.1.141-165.249 ([#208])
 * Update kernels from 6.12.31-35.92 to 6.12.35-55.103 ([#208])

[#208]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/208

# v3.1.1 (2025-06-24)

## OS Changes
 * Update kernels 5.15, 6.1 and 6.12 to the latest upstream ([#199]) ([#201])

[#199]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/199
[#201]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/201

# v3.1.0 (2025-06-11)

## OS Changes
 * Update kernels 6.1 and 6.12 to the latest upstream ([#194])
 * Include libnvidia-gpucomp.so ([#181]) Thanks, @tzmtl!

## Build Changes
 * Use SDK version v0.62.0 ([#190])

[#181]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/181
[#190]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/190
[#194]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/194

# v3.0.2 (2025-06-09)

## OS Changes
 * Update kernel 5.15 from 5.15.182 to 5.15.184 ([#185])
 * Update r570 NVIDIA driver to 570.148.08 ([#166])

[#166]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/166
[#185]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/185

# v3.0.1 (2025-06-02)

## OS Changes
 * Update kernel-6.12 from 6.12.25-32.101 to 6.12.29-33.102 ([#177])

## Build Changes
 * Fix user mapping to run the bottlerocket-sdk container in tools/latest-kernel-full-config.sh ([#175])

[#175]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/175
[#177]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/177

# v3.0.0 (2025-05-30)

## OS Changes
 * Provide Vulkan ICD configuration files for the 6.1 and 6.12 NVIDIA kmods ([#138]) Thanks, @iterion!
 * Remove GRUB's tools and modules subpackages ([#163])
 * Backport patch to ensure NUL-terminated task comm buffer ([#168])
 * Update kernel-5.15 to version 5.15.182-123.190 ([#169])

## Build Changes
 * Update nvlsm SHA value to match upstream ([#160])
 * Build GRUB with optimizations ([#163])

[#138]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/138
[#160]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/160
[#163]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/163
[#168]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/168
[#169]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/169

# v2.5.1 (2025-05-22)

## OS Changes
 * Re-enable writes to mounted block devices in kernel-6.12 to fix online resize of ext4 filesystems ([#158])

## Build Changes
 * Move kernel config script to common location and extract SDK from Twoliter metadata ([#157])

[#157]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/157
[#158]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/158

# v2.5.0 (2025-05-20)

## OS Changes
 * Provide NVLink Subnet Manager as a dependency for NVIDIA Fabric Manager ([#142])
 * Add MIG profiles for NVIDIA A100 and B200 GPUs ([#136])
 * Enable CephFS SELinux labels in kernel-6.12 ([#154]) Thanks, @vholer!

## Build Changes
 * Bump twoliter to 0.10.1 ([#150])
 * Maintain full kernel configuration for kernel-6.12 ([#114])

[#114]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/114
[#136]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/136
[#142]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/142
[#150]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/150
[#154]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/154

# v2.4.0 (2025-05-14)

## OS Changes
 * Improve dependency resolution for NVIDIA kmods ([#133])
 * Prevent version mismatches between NVIDIA kmods and kernels ([#133])
 * Strip NVIDIA open GPU and GRID kernel modules ([#139])
 * Provide nvoptix.bin through NVIDIA kmod 570 for 6.12 kernel ([#141]) Thanks, @emaincourt!
 * Enable cpusets for cgroups v1 in the 6.12 kernel ([#143])
 * Prefer LZ4 compression over LZO for zram in 6.12 kernel ([#143])
 * Make ext4 support a module for the 6.12 kernel ([#143])
 * Update 5.15, 6.1, and 6.12 kernels to the latest upstream ([#146,#147])

## Build Changes
 * Bump twoliter to 0.10.0 ([#135])

 [#133]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/133
 [#135]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/135
 [#139]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/139
 [#141]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/141
 [#143]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/143
 [#146]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/146
 [#147]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/147

# v2.3.3 (2025-05-01)

## OS Changes
 * Update kernel-6.12 to version 6.12.23-29.97 ([#129])

[#129]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/129

# v2.3.2 (2025-04-30)

## OS Changes
 * Update kernel-5.15 to version 5.15.180-122.191 ([#124])

[#124]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/124

# v2.3.1 (2025-04-29)

## OS Changes
 * Update kernel-6.1 to version 6.1.134-150.224 ([#122])

[#122]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/122

# v2.3.0 (2025-04-28)

## OS Changes
 * Drop zstd module from GRUB ([#98])
 * Update development-related packaging for kernel-6.12 and move kmod-6.12-nvidia-r570 to kernel-6.12-devel ([#99], [#118])
 * Add package definitions for NVIDIA R570 driver ([#95])
 * Update kernel-6.12 to 6.12.22 ([#110])
 * Set config options for kernel hardening ([#111])
 * Add Infiniband User MAD and autoload for Fabric Manager ([#116], [#119])
 * Add GRID drivers to kmod-6.1-nvidia-r570 and kmod-6.12-nvidia-r570 ([#113])

## Build Changes
 * Update generate kernel config scripts to fix globbing ([#109])
 * Remove force upstream for neuron ([#112])
 * Remove unused patch from kernel-6.12 ([#115])
 * Bump twoliter to 0.9.0 ([#107])

[#95]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/95
[#98]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/98
[#99]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/99
[#107]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/107
[#109]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/109
[#110]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/110
[#111]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/111
[#112]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/112
[#113]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/113
[#115]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/115
[#116]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/116
[#118]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/118
[#119]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/119

# v2.2.2 (2025-04-18)

## OS Changes
 * Update to drivers for kmod-5.15-nvidia and kmod-6.1-nvidia ([#108])

[#108]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/108

# v2.2.1 (2025-04-17)

## Build Changes
 * Update the Bottlerocket SDK to v0.61.0 ([#101])

[#101]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/101

# v2.2.0 (2025-04-17)

## OS Changes
 * Add kernel 6.12 ([#93])
 * Update to neuron 2.20.28.0 ([#96])
 * Update kernel-6.1 from 6.1.131-143.221 to 6.1.132-147.221 ([#100])
 * Update kernel-5.15 from 5.15.179-121.185 to 5.15.179-122.186 ([#100])

## Build Changes
 * Maintain full kernel configurations for kernels 5.15 and 6.1 ([#88])
 * Vend microcode supackages per vendor and platform ([#93])

[#88]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/88
[#93]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/93
[#96]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/96
[#100]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/100

# v2.1.0 (2025-04-02)

## OS Changes
 * Update kernel-6.1 from 6.1.130-139.222 to 6.1.131-143.221 ([#89])
 * Update kernel-5.15 from 5.15.178-120.187 to 5.15.179-121.185 ([#91])

## Build Changes
 * Move NVIDIA helper binaries to standard filesystem location ([#84])

[#84]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/84
[#89]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/89
[#91]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/91

# v2.0.0 (2025-03-26)

## OS Changes
 * Update kernel-5.15 to version 5.15.178-120.187 ([#81])
 * Update kernel-6.1 to version 6.1.130-139.222 ([#81])
 * Remove kernel-5.10 and kmod-5.10-nvidia ([#80])

## Build Changes
 * Update twoliter to 0.8.1 ([#77])

[#77]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/77
[#80]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/80
[#81]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/81

# v1.3.0 (2025-03-06)

## OS Changes
 * Include SHA-256 and SHA-512 CPU routines in the ARM kernel image. ([#67])

[#67]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/67

## Build Changes
 * Update twoliter to 0.8.0 ([#70])
 * Update the Bottlerocket SDK to v0.60.0. ([#71])

[#70]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/70
[#71]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/71

# v1.2.1 (2025-03-06)

## OS Changes
 * Update kernel-5.10 from 5.10.234-225.895 to 5.10.234-225.910 ([#63])
 * Update kernel-5.15 from 5.15.178-120.178 to 5.15.178-120.180 ([#63])
 * Update kernel-6.1 from 6.1.128 to 6.1.129 ([#63])

[#63]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/63

## Build Changes
 * Fix Lustre warnings in GCC 13+ ([#61])

[#61]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/61

# v1.2.0 (2025-02-26)

## Build Changes
 * Update `twoliter` from 0.7.2 to 0.7.3 ([#51])

[#51]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/51

# v1.1.4 (2025-02-25)

## OS Changes
 * Update kernel-5.10 from 5.10.233 to 5.10.234  ([#57])
 * Update kernel-5.15 from 5.15.176 to 5.15.178  ([#57])

[#57]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/57

# v1.1.3 (2025-02-24)

## OS Changes
 * Update kernel-6.1 from 6.1.127 to 6.1.128 ([#52])

[#52]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/52

# v1.1.2 (2025-02-18)

## OS Changes
 * Use NVIDIA open gpu drivers for L4 and L40S cards ([#48])
 * Remove NVIDIA Multi-Instance GPU (MIG) and Fabric Manager Interoperability code ([#49])

[#48]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/48
[#49]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/49

# v1.1.1 (2025-02-10)

## Build Changes
 * Fix the kernel-5.15 spec file to apply patches extracted from the SRPM ([#43])
 * Fail kernel builds on mismatches between the applied patches and patches found in the SRPM ([#43])
 * Update twoliter to 0.7.2 ([#36])

[#36]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/36
[#43]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/43

# v1.1.0 (2025-02-06)

## OS Changes
 * Update to kernel 6.1.127 ([#37])
 * Add support for Nvidia MIG ([#35])

## Build Changes
 * Find upstream kernel patches via the upstream source's spec file ([#40])

[#37]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/37
[#40]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/40
[#35]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/35

# v1.0.7 (2025-02-04)

## OS Changes
 * Update to kernel 5.10.233-224.894 and 5.15.176-118.178 ([#30])

[#30]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/30

# v1.0.6 (2025-01-24)

## OS Changes
 * Update to kernel 5.10.233, 5.15.176, and 6.1.124 ([#25])

[#25]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/25

# v1.0.5 (2025-01-24)

## OS Changes
 * Use the version of the driver for `kmod-*-nvidia` packages. ([#22])

## Build Changes
 * Updates the Bottlerocket SDK to v0.50.1. ([#18])

[#18]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/18
[#22]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/22

# v1.0.4 (2025-01-16)

## OS Changes
* Update neruon dkms for kernel-5.10, kernel-5.15 and kernel-6.1 ([#16], ([#17]))
* Update to drivers for kmod-5.10-nvidia, kmod-5.15-nvidia and kmod-6.1-nvidia ([#21])

[#16]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/16
[#17]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/17
[#21]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/21

# v1.0.2 (2024-12-20)

## Build Changes
* Update CHANGELOG.md to match format expected by release automation ([#12])

[#12]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/12

# v1.0.1 (2024-12-20)

## OS Changes
* Update to kernel 5.10.230 and 5.15.173 ([#10])

## Build Changes
* Add GPG verification where possible ([#5])

[#5]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/5
[#10]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/10

# v1.0.0 (2024-12-11)

## Build Changes
* Create the new kernel kit from the following core-kit packages: ([#1])
  * grub
  * kernel-5.10
  * kernel-5.15
  * kernel-6.1
  * kmod-5.10-nvidia
  * kmod-5.15-nvidia
  * kmod-6.1-nvidia
  * libkcapi
  * linux-firmware
  * microcode
  * shim
* Update bottlerocket-sdk to v0.50.0

[#1]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/1
