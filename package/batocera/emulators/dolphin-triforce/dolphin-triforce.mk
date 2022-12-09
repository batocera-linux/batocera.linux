################################################################################
#
# DOLPHIN TRIFORCE
#
################################################################################
# This is a build that is no longer receiving updates. AppImage format ensures compatibility into the future.
# Site https://dolphin-emu.org/download/list/Triforce/1/
# Source https://github.com/EIGHTFINITE/dolphin-triforce
# Dolphin version: 4.0-315
DOLPHIN_TRIFORCE_SOURCE = 
DOLPHIN_TRIFORCE_VERSION = 1.0.0-001
DOLPHIN_TRIFORCE_LICENSE = GPLv2+

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	DOLPHIN_TRIFORCE_DEPENDENCIES = xserver_xorg-server
endif

# Includes custom game configs required to successfully launch and play them.
define DOLPHIN_TRIFORCE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0555 "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-triforce/dolphin-triforce.AppImage" "${TARGET_DIR}/usr/bin/dolphin-triforce"
endef

# Hotkeys (non-functional at the moment)
define DOLPHIN_TRIFORCE_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-triforce/triforce.dolphin_triforce.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

DOLPHIN_TRIFORCE_POST_INSTALL_TARGET_HOOKS = DOLPHIN_TRIFORCE_EVMAP

$(eval $(generic-package))
