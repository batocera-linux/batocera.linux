################################################################################
#
# uboot files for rock960
#
################################################################################
UBOOT_ROCK960_VERSION = 1
UBOOT_ROCK960_SOURCE = uboot-rock960-2020.07.tar.gz
UBOOT_ROCK960_SITE = https://github.com/batocera-linux/batocera.linux/releases/download/uboot-rock960

define UBOOT_ROCK960_INSTALL_TARGET_CMDS
	cp $(@D)/u-boot.bin    $(BINARIES_DIR)/u-boot-rock960.bin
	cp $(@D)/u-boot.itb    $(BINARIES_DIR)/u-boot-rock960.itb
	cp $(@D)/idbloader.img $(BINARIES_DIR)/idbloader-rock960.img
endef

$(eval $(generic-package))
