################################################################################
#
# cemu
#
################################################################################

CEMU_VERSION = 2.0
CEMU_SOURCE = cemu-$(CEMU_VERSION)-ubuntu-20.04-x64.zip
CEMU_SITE = https://github.com/cemu-project/Cemu/releases/download/v$(CEMU_VERSION)
CEMU_LICENSE = mpl-2.0

define CEMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(CEMU_DL_SUBDIR)/$(CEMU_SOURCE)
endef

define CEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/cemu/
	cp -prn $(@D)/Cemu_$(CEMU_VERSION)/{Cemu,gameProfiles,resources} $(TARGET_DIR)/usr/cemu/
	# keys.txt
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu
	touch $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu/keys.txt
	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/cemu/wiiu.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
