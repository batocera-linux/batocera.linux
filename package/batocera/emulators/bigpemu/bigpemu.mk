################################################################################
#
# bigpemu
#
################################################################################

BIGPEMU_VERSION = v1092
BIGPEMU_SOURCE = BigPEmu_$(BIGPEMU_VERSION).zip
BIGPEMU_SITE = https://www.richwhitehouse.com/jaguar/builds

define BIGPEMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(BIGPEMU_DL_SUBDIR)/$(BIGPEMU_SOURCE)
endef

define BIGPEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bigpemu
	cp -pr $(@D)/* $(TARGET_DIR)/usr/bigpemu/
	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/bigpemu/jaguar.bigpemu.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
