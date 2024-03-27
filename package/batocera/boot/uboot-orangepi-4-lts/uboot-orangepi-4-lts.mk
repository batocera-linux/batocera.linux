################################################################################
#
# uboot files for OrangePi 4 LTS
#
################################################################################

UBOOT_ORANGEPI_4_LTS_VERSION = 2022.04-armbian
UBOOT_ORANGEPI_4_LTS_SOURCE =

define UBOOT_ORANGEPI_4_LTS_BUILD_CMDS
endef

define UBOOT_ORANGEPI_4_LTS_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-4-lts
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-4-lts/idbloader.bin $(BINARIES_DIR)/uboot-orangepi-4-lts/idbloader.bin
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-4-lts/trust.bin $(BINARIES_DIR)/uboot-orangepi-4-lts/trust.bin
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-orangepi-4-lts/uboot.img $(BINARIES_DIR)/uboot-orangepi-4-lts/u-boot.img
endef

$(eval $(generic-package))
