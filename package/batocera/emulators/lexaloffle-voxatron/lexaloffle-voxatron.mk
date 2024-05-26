################################################################################
#
# Voxatron official virtuel console (needs the binary, not part of Batocera) 
#
################################################################################
LEXALOFFLE_VOXATRON_VERSION = 0.1
LEXALOFFLE_VOXATRON_LICENSE = proprietary-commercial
LEXALOFFLE_VOXATRON_SOURCE = 

define LEXALOFFLE_VOXATRON_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lexaloffle-voxatron/voxatron.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
