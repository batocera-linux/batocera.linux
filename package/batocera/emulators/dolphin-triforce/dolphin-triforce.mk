################################################################################
#
# DOLPHIN TRIFORCE
#
################################################################################
# This is a build that is no longer receiving updates. AppImage format ensures compatibility into the future.
# Site https://dolphin-emu.org/download/list/Triforce/1/
# Source https://github.com/EIGHTFINITE/dolphin-triforce
DOLPHIN_TRIFORCE_SOURCE = 
DOLPHIN_TRIFORCE_VERSION = 4.0-315
DOLPHIN_TRIFORCE_LICENSE = GPLv2+

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	DOLPHIN_TRIFORCE_DEPENDENCIES = xserver_xorg-server
endif

# Includes custom game configs required to successfully launch and play them.
define DOLPHIN_TRIFORCE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0555 "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-triforce/dolphin-triforce.AppImage" "${TARGET_DIR}/usr/bin/dolphin-triforce.AppImage"
	mkdir -p $(TARGET_DIR)/usr/share/dolphin-triforce/sys/GameSettings/
	cp -f "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-triforce/GGPE01.ini" "${TARGET_DIR}/usr/share/dolphin-triforce/sys/GameSettings/GGPE01.ini"
	cp -f "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-triforce/GGPE02.ini" "${TARGET_DIR}/usr/share/dolphin-triforce/sys/GameSettings/GGPE02.ini"
endef

$(eval $(generic-package))
