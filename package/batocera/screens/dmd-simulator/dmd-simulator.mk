################################################################################
#
# DMD_SIMULATOR
#
################################################################################
DMD_SIMULATOR_VERSION = fd1d4b1c7e96cd679c2431ff2ee56506c193f0a0
DMD_SIMULATOR_SITE =  $(call github,batocera-linux,dmd-simulator,$(DMD_SIMULATOR_VERSION))

define DMD_SIMULATOR_INSTALL_DMD_SIMULATOR
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(@D)/dmd-simulator.py $(TARGET_DIR)/usr/bin/dmd-simulator
endef

define DMD_SIMULATOR_INSTALL_DMD_SIMULATOR_PLAYER
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(@D)/dmd-play.py      $(TARGET_DIR)/usr/bin/dmd-play

        mkdir -p $(TARGET_DIR)/usr/share/dmd-simulator/scripts
        $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/scripts/*.sh $(TARGET_DIR)/usr/share/dmd-simulator/scripts/

        mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/dmd_simulator.service $(TARGET_DIR)/usr/share/batocera/services/dmd_simulator

	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/batocera.png $(TARGET_DIR)/usr/share/dmd-simulator/images/system/batocera.png
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/dmd-simulator/rainbow.png $(TARGET_DIR)/usr/share/dmd-simulator/images/system/rainbow.png
endef

ifeq ($(BR2_PACKAGE_DMD_SIMULATOR),y)
	DMD_SIMULATOR_POST_INSTALL_TARGET_HOOKS += DMD_SIMULATOR_INSTALL_DMD_SIMULATOR
endif

ifeq ($(BR2_PACKAGE_DMD_SIMULATOR_PLAYER),y)
	DMD_SIMULATOR_POST_INSTALL_TARGET_HOOKS += DMD_SIMULATOR_INSTALL_DMD_SIMULATOR_PLAYER
endif

$(eval $(generic-package))
