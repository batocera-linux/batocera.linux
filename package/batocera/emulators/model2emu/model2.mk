################################################################################
#
# model 2 emulator
#
################################################################################

# version 1.1a - closed source
# not developed since 2014
MODEL2EMU_SOURCE = m2emulator.zip
MODEL2EMU_SITE = http://nebula.emulatronia.com/files

define MODEL2EMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(MODEL2EMU_DL_SUBDIR)/$(MODEL2EMU_SOURCE)
endef

define MODEL2EMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/model2emu
	cp -pr $(@D) $(TARGET_DIR)/usr

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/model2emu/model2emu.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
