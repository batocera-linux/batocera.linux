################################################################################
#
# Pico-8 official virtuel console (needs the binary, not part of Batocera) 
#
################################################################################
LEXALOFFLE_PICO8_VERSION = 0.1
LEXALOFFLE_PICO8_LICENSE = proprietary-commercial
LEXALOFFLE_PICO8_SOURCE = 

define LEXALOFFLE_PICO8_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lexaloffle-pico8/pico8.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
