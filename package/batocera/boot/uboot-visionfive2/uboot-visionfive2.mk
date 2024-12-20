################################################################################
#
# uboot-visionfive2
#
################################################################################

UBOOT_VISIONFIVE2_VERSION = 3.6.1
UBOOT_VISIONFIVE2_SITE = \
    https://github.com/starfive-tech/VisionFive2/releases/download/VF2_v$(UBOOT_VISIONFIVE2_VERSION)
UBOOT_VISIONFIVE2_SOURCE = u-boot-spl.bin.normal.out
UBOOT_VISIONFIVE2_EXTRA_DOWNLOADS = visionfive2_fw_payload.img

define UBOOT_VISIONFIVE2_EXTRACT_CMDS
endef

define UBOOT_VISIONFIVE2_BUILD_CMDS
endef

define UBOOT_VISIONFIVE2_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-visionfive2
	cp $(UBOOT_VISIONFIVE2_DL_DIR)/u-boot-spl.bin.normal.out \
	    $(BINARIES_DIR)/uboot-visionfive2/u-boot-spl.bin.normal.out
	cp $(UBOOT_VISIONFIVE2_DL_DIR)/visionfive2_fw_payload.img \
	    $(BINARIES_DIR)/uboot-visionfive2/visionfive2_fw_payload.img
endef

$(eval $(generic-package))
