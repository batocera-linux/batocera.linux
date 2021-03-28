################################################################################
#
# uboot files for rockpro64
#
################################################################################
UBOOT_ROCKPRO64_VERSION = 1
UBOOT_ROCKPRO64_SOURCE = uboot-rockpro64-2020.07.tar.gz
UBOOT_ROCKPRO64_SITE = https://github.com/batocera-linux/batocera.linux/releases/download/uboot-rockpro64

define UBOOT_ROCKPRO64_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin    $(BINARIES_DIR)/u-boot-rockpro64.bin
	cp $(@D)/u-boot.itb    $(BINARIES_DIR)/u-boot-rockpro64.itb
	cp $(@D)/idbloader.img $(BINARIES_DIR)/idbloader-rockpro64.img
endef

$(eval $(generic-package))
