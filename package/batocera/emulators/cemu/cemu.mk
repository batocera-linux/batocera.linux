################################################################################
#
# Cemu
#
################################################################################

# version 1.21.5
CEMU_VERSION = 1.21.5
CEMU_SOURCE = cemu_$(CEMU_VERSION).zip
CEMU_SITE = https://cemu.info/releases

define CEMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(CEMU_DL_SUBDIR)/$(CEMU_SOURCE)
endef

define CEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/userdata/system/cemu/
	cp -prn $(@D)/cemu_$(CEMU_VERSION)/{Cemu.exe,gameProfiles,resources} $(TARGET_DIR)/userdata/system/cemu/

	# settings
	ln -sf /userdata/system/configs/cemu/settings.xml $(TARGET_DIR)/userdata/system/cemu/settings.xml

	# keys.txt
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu
	touch $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu/keys.txt
	ln -sf /userdata/bios/cemu/keys.txt $(TARGET_DIR)/userdata/system/cemu/keys.txt

	# logs
	ln -sf /userdata/system/configs/cemu/log.txt $(TARGET_DIR)/userdata/system/cemu/log.txt

	# subdirs config
	ln -sf /userdata/system/configs/cemu/shaderCache $(TARGET_DIR)/userdata/system/cemu/shaderCache
	ln -sf /userdata/system/configs/cemu/controllerProfiles $(TARGET_DIR)/userdata/system/cemu/controllerProfiles
	ln -sf /userdata/system/configs/cemu/graphicPacks $(TARGET_DIR)/userdata/system/cemu/graphicPacks
	
	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/wiiu.keys $(TARGET_DIR)/usr/share/evmapy

endef

$(eval $(generic-package))
