################################################################################
#
# Cemu
#
################################################################################

# version 1.22.1
CEMU_VERSION = 1.22.1
CEMU_SOURCE = cemu_$(CEMU_VERSION).zip
CEMU_SITE = https://cemu.info/releases

define CEMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(CEMU_DL_SUBDIR)/$(CEMU_SOURCE)
endef

define CEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/cemu/
	cp -prn $(@D)/cemu_$(CEMU_VERSION)/{Cemu.exe,gameProfiles,resources} $(TARGET_DIR)/usr/cemu/

	# settings - can't be a link while cemu remove it
	#ln -sf /userdata/system/configs/cemu/settings.xml $(TARGET_DIR)/usr/cemu/settings.xml

	# keys.txt
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu
	touch $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu/keys.txt
	ln -sf /userdata/bios/cemu/keys.txt $(TARGET_DIR)/usr/cemu/keys.txt

	# logs
	ln -sf /userdata/system/configs/cemu/log.txt $(TARGET_DIR)/usr/cemu/log.txt

	# subdirs config
	ln -sf /userdata/system/configs/cemu/shaderCache $(TARGET_DIR)/usr/cemu/shaderCache
	ln -sf /userdata/system/configs/cemu/controllerProfiles $(TARGET_DIR)/usr/cemu/controllerProfiles
	ln -sf /userdata/system/configs/cemu/graphicPacks $(TARGET_DIR)/usr/cemu/graphicPacks
	
	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/cemu/wiiu.keys $(TARGET_DIR)/usr/share/evmapy

endef

$(eval $(generic-package))
