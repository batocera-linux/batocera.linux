################################################################################
#
# firmware-khadas-vim4
#
################################################################################

FIRMWARE_KHADAS_VIM4_VERSION = 1.0
FIRMWARE_KHADAS_VIM4_SITE =
FIRMWARE_KHADAS_VIM4_SOURCE =
FIRMWARE_KHADAS_VIM4_FIRMWARE_DIR = $(TARGET_DIR)/lib/firmware

define FIRMWARE_KHADAS_VIM4_BUILD_CMDS
endef

define FIRMWARE_KHADAS_VIM4_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/firmware-khadas-vim4/firmware/* $(FIRMWARE_KHADAS_VIM4_FIRMWARE_DIR)/
endef

$(eval $(generic-package))
