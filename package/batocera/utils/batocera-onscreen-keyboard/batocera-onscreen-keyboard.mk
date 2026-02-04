################################################################################
#
# batocera-onscreen-keyboard
#
################################################################################
# wvkbd - On-screen keyboard for wlroots
# Converted from ROCKNIX touchscreen-keyboard package
################################################################################

BATOCERA_ONSCREEN_KEYBOARD_VERSION = v0.17
BATOCERA_ONSCREEN_KEYBOARD_SITE = $(call github,jjsullivan5196,wvkbd,$(BATOCERA_ONSCREEN_KEYBOARD_VERSION))
BATOCERA_ONSCREEN_KEYBOARD_LICENSE = GPL-3.0+
BATOCERA_ONSCREEN_KEYBOARD_LICENSE_FILES = LICENSE

BATOCERA_ONSCREEN_KEYBOARD_DEPENDENCIES = wayland pango libxkbcommon cairo host-pkgconf

BATOCERA_ONSCREEN_KEYBOARD_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-onscreen-keyboard

# Build using make
# Patch 003 makes wvkbd respect PKG_CONFIG variable for cross-compilation
define BATOCERA_ONSCREEN_KEYBOARD_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CC="$(TARGET_CC)" \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		wvkbd-mobintl
endef

define BATOCERA_ONSCREEN_KEYBOARD_INSTALL_TARGET_CMDS
	# Install the keyboard binary to libexec (helper binary)
	$(INSTALL) -D -m 0755 $(@D)/wvkbd-mobintl \
		$(TARGET_DIR)/usr/libexec/onscreen-keyboard/wvkbd-mobintl

	# Install the main toggle script (user-facing)
	$(INSTALL) -D -m 0755 $(BATOCERA_ONSCREEN_KEYBOARD_PATH)/sources/onscreen-keyboard \
		$(TARGET_DIR)/usr/bin/onscreen-keyboard

	# Install the toggle alias for Control Center compatibility
	ln -sf onscreen-keyboard $(TARGET_DIR)/usr/bin/onscreen-keyboard-toggle

	# Install assets directory
	mkdir -p $(TARGET_DIR)/usr/share/onscreen-keyboard

	$(INSTALL) -D -m 0755 $(BATOCERA_ONSCREEN_KEYBOARD_PATH)/sources/touchscreen-detect.py \
		$(TARGET_DIR)/usr/bin/touchscreen-detect

endef

$(eval $(generic-package))
