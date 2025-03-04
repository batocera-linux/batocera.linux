################################################################################
#
# uboot files for SM8550
#
################################################################################

UBOOT_SM8550_VERSION = 5698f9a3520107d6fd0cf5440db8fba0a477b0c7
UBOOT_SM8550_SITE = $(call github,AYNTechnologies,u-boot,$(UBOOT_SM8550_VERSION))
UBOOT_SM8550_DEPENDENCIES = host-xxd # libgnutls28-dev mkbootimg

define UBOOT_SM8550_BUILD_CMDS
    cd $(@D) && CROSS_COMPILE=$(HOST_DIR)/bin/aarch64-buildroot-linux-gnu- make O=.output qcom_defconfig
    cd $(@D) && PATH="$(HOST_DIR)/bin:$$PATH" CROSS_COMPILE=$(HOST_DIR)/bin/aarch64-buildroot-linux-gnu- make O=.output DEVICE_TREE=qcom/qcs8550-ayn-odin2-common
    cd $(@D) && gzip .output/u-boot-nodtb.bin -c > .output/u-boot-nodtb.bin.gz
    cd $(@D) && cat .output/u-boot-nodtb.bin.gz .output/dts/upstream/src/arm64/qcom/qcs8550-ayn-odin2-common.dtb > .output/kernel-dtb
    cd $(@D) && mkbootimg --kernel_offset '0x00008000' --pagesize '4096' --kernel .output/kernel-dtb -o .output/u-boot.img --cmdline "nodtbo"
endef

define UBOOT_SM8550_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-sm8550/
	cp $(@D)/.output/u-boot.img $(BINARIES_DIR)/uboot-sm8550/u-boot.img
endef

$(eval $(generic-package))
