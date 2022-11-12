# U-Boot packages

U-Boot packages in this directory are organized as follows:

- `Config.in` in this directory:
  - Sets the default U-Boot version for all U-Boot builds.
  - Sources all next level subdirectory `Config.in` files and selects correct
    package(s) based on `BR2_PACKAGE_BATOCERA_TARGET_xxx` variables.
- Every directory in this directory (including itself):
  - Has `uboot.config.fragment` containing U-Boot configuration (can be empty).
    These files are picked up by build in "closer to root first" order to form
    final U-Boot configuration.
  - Can have `*.patch` files to be applied to U-Boot builds in "closer to root
    first" order.
- Subdirectories have SoC specific packages with SoC specific configs and
  patches.
- SoC specific packages source and select board specific packages.
- Board specific packages do the actual work as they:
  - Apply all found patches in "closer to root first" order starting from this
    directory.
  - Gather all `uboot.config.fragment` files in "closer to root first" order
    starting from this directory.
  - Build board specific U-Boot using `kconfig-package` infrastructure.

## arm-trusted-firmware package (Trusted Firmware-A)

`arm-trusted-firmware` package (and it's selectable configs) is selected by SoC
specific packages. Any extra configs for `arm-trusted-firmware` is done in the
`xxx.board` file. For example:

```
# in file: configs/batocera-rk3399.board
BR2_TARGET_ARM_TRUSTED_FIRMWARE_PLATFORM="rk3399"
BR2_TARGET_ARM_TRUSTED_FIRMWARE_IMAGES="bl31/bl31.elf"
```

## Bumping U-Boot

In simplest case just update `BR2_PACKAGE_UBOOT_COMMON_VERSION` in this
directory's `Config.in` or set it in the `xxx.board` file. For example:

```
# in file: package/batocera/boot/uboot-common/Config.in
config BR2_PACKAGE_UBOOT_COMMON_VERSION
  string "u-boot version"
  default "2023.01"

# or in file: configs/batocera-rk3399.board
BR2_PACKAGE_UBOOT_COMMON_VERSION="2023.01"
```

In case one SoC requires different version set it in the `xxx.board` file. For
example:

```
# in file: configs/batocera-rk3399.board
BR2_PACKAGE_UBOOT_RK3399_VERSION="2022.10"
```

In case one board requires different version set it in the `xxx.board` file.
For example:

```
# in file: configs/batocera-rk3399.board
BR2_PACKAGE_UBOOT_ROCKPRO64_VERSION="2022.10"
```
