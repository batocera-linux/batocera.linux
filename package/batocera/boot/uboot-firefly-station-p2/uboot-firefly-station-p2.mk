################################################################################
#
# uboot files for Firefly Station P2
#
################################################################################

UBOOT_FIREFLY_STATION_P2_VERSION = 1.0
UBOOT_FIREFLY_STATION_P2_SOURCE =

define UBOOT_FIREFLY_STATION_P2_BUILD_CMDS
endef

define UBOOT_FIREFLY_STATION_P2_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-firefly-station-p2
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-firefly-station-p2/idbloader.img $(BINARIES_DIR)/uboot-firefly-station-p2/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-firefly-station-p2/uboot.img $(BINARIES_DIR)/uboot-firefly-station-p2/uboot.img
endef

$(eval $(generic-package))
