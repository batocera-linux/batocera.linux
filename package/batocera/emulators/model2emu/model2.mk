################################################################################
#
# model2emu
#
################################################################################

# version 1.1a - closed source
# not developed since 2014
MODEL2EMU_SOURCE = m2emulator.zip
# source location updated since previous website is now unavailable
MODEL2EMU_SITE = https://github.com/batocera-linux/model2emu/raw/main

define MODEL2EMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(MODEL2EMU_DL_SUBDIR)/$(MODEL2EMU_SOURCE)
endef

define MODEL2EMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/model2emu
	cp -pr $(@D) $(TARGET_DIR)/usr
	# extra files
	unzip -uo $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/model2emu/model2scripts.zip -d $(TARGET_DIR)/usr/model2emu/

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/model2emu/model2.model2emu.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
