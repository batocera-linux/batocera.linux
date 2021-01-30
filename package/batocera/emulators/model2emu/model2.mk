################################################################################
#
# model 2 emulator
#
################################################################################

MODEL2EMU_SOURCE = http://nebula.emulatronia.com/files/m2emulator.zip

define MODEL2EMU_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && unzip $(DL_DIR)/$(MODEL2EMU_DL_SUBDIR)/$(MODEL2EMU_SOURCE)
endef

define MODEL2EMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/model2emu
	cp -pr $(@D)/target/model2emu/m2emulator $(TARGET_DIR)/usr/model2emu

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/model2emu/model2emu.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
