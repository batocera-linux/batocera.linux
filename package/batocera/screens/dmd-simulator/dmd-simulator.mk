################################################################################
#
# DMD_SIMULATOR
#
################################################################################
DMD_SIMULATOR_VERSION = 6298b07d0a083f4531236adb54d4d272e82f297b
DMD_SIMULATOR_SITE =  $(call github,batocera-linux,dmd-simulator,$(DMD_SIMULATOR_VERSION))
DMD_SIMULATOR_SETUP_TYPE = pep517
DMD_SIMULATOR_DEPENDENCIES = host-python-hatchling

define DMD_SIMULATOR_DMD_PLAY_SYMLINK
       ln -sf dmd-play-python $(TARGET_DIR)/usr/bin/dmd-play
endef

ifeq ($(BR2_PACKAGE_DMD_SIMULATOR_DMD_PLAY_BIN),y)
DMD_SIMULATOR_POST_INSTALL_TARGET_HOOKS += DMD_SIMULATOR_DMD_PLAY_SYMLINK
endif

define DMD_SIMULATOR_INSTALL_DMD_SIMULATOR_PLAYER
        mkdir -p $(TARGET_DIR)/usr/share/dmd-simulator/scripts
        $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/scripts/*.sh $(TARGET_DIR)/usr/share/dmd-simulator/scripts/

        mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/dmd_simulator.service $(TARGET_DIR)/usr/share/batocera/services/dmd_simulator

	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/batocera.png $(TARGET_DIR)/usr/share/dmd-simulator/images/system/batocera.png
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/rainbow.png $(TARGET_DIR)/usr/share/dmd-simulator/images/system/rainbow.png
endef

ifeq ($(BR2_PACKAGE_DMD_SIMULATOR_PLAYER),y)
	DMD_SIMULATOR_POST_INSTALL_TARGET_HOOKS += DMD_SIMULATOR_INSTALL_DMD_SIMULATOR_PLAYER
endif

$(eval $(python-package))
