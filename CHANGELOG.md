# v5.3.0 (2026-03-24)

## OS Changes
* Add kernel 6.18 ([#381])

[#381]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/381

# v5.2.0 (2026-03-18)
## Build Changes
* Update the Bottlerocket SDK to v0.72.0 ([#391])

[#391]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/391

# v5.1.0 (2026-03-17)
## OS Changes
* Add Neuron driver 2.x.7372.0, 2.x.7693.0, and 2.x.8072.0 ([#388])
* Update Neuron driver to 2.24.13.0, and 2.26.10.0 ([#389])

## Build Changes
* Update the Bottlerocket SDK to v0.71.0 ([#387])

[#387]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/387
[#388]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/388
[#389]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/389

# v5.0.2 (2026-03-06)
## OS Changes
* Update kernel from 6.1.161-183.298 to 6.1.163-186.299 ([#384])
* Update kernel from 6.12.68-92.122 to 6.12.73-95.123 ([#383])
* Update EFA driver to 3.0.0 ([#380])

## Build Changes
* Bump Twoliter to 0.17.0 ([#379])

[#379]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/379
[#380]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/380
[#383]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/383
[#384]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/384

# v5.0.1 (2026-02-26)
## OS Changes
* Fix WireGuard regression affecting Cilium pod connectivity ([#375])
* Update Neuron driver to 2.26.5.0 ([#377])

[#375]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/375
[#377]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/377

# v5.0.0 (2026-02-19)
## OS Changes
* Remove EOL r570 NVIDIA driver ([#370])
* Update kernel from 6.12.66-88.122 to 6.12.68-92.122 ([#372])

## Build Changes
* Bump cargo dependencies ([#371])

[#370]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/370
[#371]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/371
[#372]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/372

# v4.8.2 (2026-02-07)
## OS Changes
* Update kernel from 6.1.159-182.297 to 6.1.161-183.298 ([#366])
* Update kernel from 6.12.64-87.122 to 6.12.66-88.122 ([#367])

[#366]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/366
[#367]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/367

# v4.8.1 (2026-01-23)
## OS Changes
* Update kernel from 6.1.159-181.297 to 6.1.159-182.297 ([#360])
* Update kernel from 6.12.63-84.121 to 6.12.64-87.122 ([#359])

[#360]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/359
[#359]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/360

# v4.8.0 (2026-01-21)
## OS Changes
* Add MPS subpackage to NVIDIA kmod packages ([#347])
* Update r570 NVIDIA driver to 570.211.01 ([#357])
* Update r580 NVIDIA driver to 580.126.09 ([#357])
* Disable ext4 debugging for 6.12 kernel ([#356])

## Build Changes
* Update the Bottlerocket SDK to v0.70.0 ([#358])

[#347]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/347
[#356]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/356
[#357]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/357
[#358]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/358

# v4.7.1 (2026-01-07)
## OS Changes
* Add dependency on the GRID license for NVIDIA k8s device plugin ([#294])
* Update Neuron driver to 2.25.4.0 ([#344], [#350])
* Adjust BOOT_IMAGE for PCR 9 predictions ([#343])
* Fix typo in NVLSM service ([#351])
* Update kernel from 6.1.158-180.294 to 6.1.159-181.297 ([#353])
* Update kernel from 6.12.58-82.121 to 6.12.63-84.121 ([#348],[#352])

## Build Changes
* Clean up NVIDIA kmod spec files ([#341])
* Update twoliter to 0.16.0 ([#342], [#349])
* Override SBOM generation for nvidia-migmanager ([#346])

[#294]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/294
[#341]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/341
[#342]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/342
[#343]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/343
[#344]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/344
[#346]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/346
[#348]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/348
[#349]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/349
[#350]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/350
[#351]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/351
[#352]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/352
[#353]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/353

# v4.7.0 (2025-12-11)
## Build Changes
* Update the Bottlerocket SDK to v0.66.0 ([#336])

[#336]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/336 

# v4.6.1 (2025-12-09)
## OS Changes
* Update kernel from 6.1.158-178.288 to 6.1.158-180.294 ([#332])
* Update kernel from 6.12.55-74.119 to 6.12.58-82.121 ([#333])

## Build Changes
* Update to Twoliter 0.14.0 ([#331])
* Update libkcapi `_spec_install_post` override for SBOM feature compatibility ([#330])

[#330]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/330
[#331]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/331
[#332]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/332
[#333]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/333

# v4.6.0 (2025-12-05)
## OS Changes
* Add package definition for NVIDIA R580 driver for kernel-6.1 ([#304]). Thanks, @mselim00!
* Provide EFA kernel modules as kmod packages ([#319], [#322], [#327])
* Add kmod-6.12-amdgpu package and update linux-firmware ([#320], [#325], [#326])
* Load NVIDIA kmods at `drivers.target` ([#321])
* Extend supported MIG profiles for NVIDIA B300 ([#323])

## Build Changes
* Scope down GitHub Token permissions ([#298]). Thanks, @AdnaneKhan!

[#298]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/298
[#304]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/304
[#319]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/319
[#320]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/320
[#321]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/321
[#322]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/322
[#323]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/323
[#325]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/325
[#326]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/326
[#327]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/327

# v4.5.1 (2025-11-12)
## OS Changes
* Include EFA from efa-installer in kernel-6.12 ([#313])

## Build Changes
* Update to Twoliter 0.13.0 ([#315])

[#313]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/313
[#315]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/315

# v4.5.0 (2025-11-10)
## OS Changes
* Update kernel from 6.1.156-177.286 to 6.1.158-178.288([#310])
* Update kernel from to 6.12.53-69.119 to 6.12.55-74.119 ([#311])
* Add additional Neuron module in 6.1 and 6.12 Kernels ([#277])
* Add RTX PRO 6000 profiles ([#300])
* Disable PCR 9 measurement in 6.1 and 6.12 Kernels ([#305])

[#277]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/277
[#300]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/300
[#305]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/305
[#310]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/310
[#311]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/311

# v4.4.2 (2025-10-27)
## OS Changes
* Update kernel from 6.1.155-176.282 to 6.1.156-177.286 ([#302])
* Update kernel from 6.12.46-66.121 to 6.12.53-69.119 ([#301])

[#302]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/302
[#301]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/301

# v4.4.1 (2025-10-22)

## Build Changes
* Update the Bottlerocket SDK to v0.65.1 ([#299])

[#299]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/299

# v4.4.0 (2025-10-16)
## OS Changes
* Move netfilter modules to built-in ([#296])

## Build Changes
* Update the Bottlerocket SDK to v0.65.0 ([#295])

[#295]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/295
[#296]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/296

# v4.3.4 (2025-10-14)
## OS Changes
* Update kernel from 6.1.153-175.280 to 6.1.155-176.282 ([#290])

## Build Changes
* Fully containerize latest-kernel-full-config.sh ([#258], [#288], [#289])

[#258]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/258
[#288]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/288
[#289]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/289
[#290]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/290

# v4.3.3 (2025-10-03)
## OS Changes
* Update r570 NVIDIA driver to 570.195.03 ([#283])
* Update r580 NVIDIA driver to 580.95.05 ([#283])
* Update nvlsm to 2025.06.6 ([#283])
* Provide nvidia-gridd as a system service ([#285])

[#283]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/283
[#285]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/285

# v4.3.2 (2025-09-29)
## OS Changes
* Update kernel from 6.1.150-174.273 to 6.1.153-175.280 ([#279])
* Update kernel from 6.12.40-64.114 to 6.12.46-66.121 ([#280])

[#279]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/279
[#280]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/280

# v4.3.1 (2025-09-15)
## OS Changes
* Update kernel from 6.1.148-173.267 to 6.1.150-174.273 ([#274])

## Build Changes
* Split kernel configurations per architecture ([#266])
* Improve Bottlerocket's final kernel configuration validation ([#266])
* Exclude Neuron modules from all NVIDIA flavors ([#273]) Thanks, @fletcherw!

[#266]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/266
[#273]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/273
[#274]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/274

# v4.3.0 (2025-09-08)
## OS Changes
* Update kernel from 6.1.147-172.266 to 6.1.148-173.267 ([#268])
* Update kernel from 6.12.40-63.114 to 6.12.40-64.114 ([#269], [#270], [#271])
* Add package definitions for NVIDIA R580 driver ([#255])
* Enable FIPS support for kernel-6.12 ([#263])

## Build Changes
* Generate full kernel configuration in the Bottlerocket SDK ([#247])

[#247]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/247
[#255]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/255
[#263]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/263
[#268]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/268
[#269]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/269
[#270]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/270
[#271]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/271

# v4.2.0 (2025-08-25)
## OS Changes
* Update to neuron 2.21.37.0 ([#250])
* Backport patch to prevent race with lease breaks in SMB's ([#253])

## Build Changes
* Updated to Twoliter 0.12.0 ([#251])

[#250]:https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/250
[#251]:https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/251
[#253]:https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/253

# v4.1.0 (2025-08-19)
## OS Changes
* Provide missing kernel module details for r570 Tesla drivers in 6.12 ([#234])
* Enable SCSI for VMware ([#237])

## Build Changes
* Update the Bottlerocket SDK to v0.64.0 ([#248])

[#234]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/234
[#237]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/237
[#248]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/248

# v4.0.1 (2025-08-11)
## OS Changes
 * Update kernel from 6.12.40-63.107 to 6.12.40-63.114 ([#239])
 * Update kernel from 6.1.147-172.259 to 6.1.147-172.266 ([#240])

[#239]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/239
[#240]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/240

# v4.0.0 (2025-08-04)
## OS Changes
 * Drop kernel 5.15 and R535 NVIDIA kmod packages ([#226])
 * Update grub and shim packages ([#228])
 * Update kernel from 6.12.37-61.105 to 6.12.40-63.107 ([#229])
 * Update kernel from 6.1.144-170.251 to 6.1.147-172.259  ([#230])

[#226]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/226
[#228]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/228
[#229]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/229
[#230]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/230

# v3.3.1 (2025-07-25)
## OS Changes
 * Update r570 NVIDIA driver to 570.172.08 ([#223])
 * Update r535 NVIDIA driver to 535.261.03 ([#223])

[#223]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/223

# v3.3.0 (2025-07-23)
## Build Changes
* Updated to Twoliter 0.11.0 ([#215])

## OS Chnages
* Update kernels from 5.15.186 to 5.15.187-130.192 ([#219])
* Update kernels from 6.1.141-165.249 to 6.1.144-170.251 ([#217])
* Update kernels from 6.12.31-35.92 to 6.12.37-61.105 ([#218])
* Update 6.1 kernel config to more closely match 6.12 ([#216])
* Enable Landlock LSM in 6.1 and 6.12 kernels ([#216])
* Add IMEX for 6.12 NVIDIA R570 driver ([#204])

[#204]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/204
[#215]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/215
[#216]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/216
[#217]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/217
[#218]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/218
[#219]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/219

# v3.2.1 (2025-07-24)

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
