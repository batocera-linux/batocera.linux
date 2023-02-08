################################################################################
#
# sway
#
################################################################################

SWAY_VERSION = 1.8
SWAY_SITE = $(call github,swaywm,sway,$(SWAY_VERSION))
SWAY_LICENSE = MIT
SWAY_LICENSE_FILES = LICENSE
SWAY_DEPENDENCIES = wlroots cairo pango libglib2 pcre2 gdk-pixbuf grim wf-recorder

SWAY_CONF_OPTS = -Ddefault-wallpaper=false \
                -Dzsh-completions=false \
                -Dbash-completions=false \
                -Dfish-completions=false \
                -Dswaybar=false \
                -Dswaynag=false \
                -Dtray=disabled \
                -Dman-pages=disabled \
                -Dgdk-pixbuf=enabled

ifeq ($(BR2_PACKAGE_XWAYLAND),y)
SWAY_CONF_OPTS += -Dxwayland=enabled
else
SWAY_CONF_OPTS += -Dxwayland=disabled
endif

# sway does not build without -Wno flags as all warnings being treated as errors
SWAY_CFLAGS = $(TARGET_CFLAGS) -Wno-unused-variable -Wno-unused-but-set-variable -Wno-unused-function -Wno-maybe-uninitialized -Wno-stringop-truncation -Wno-address

define SWAY_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    $(INSTALL) -D $(@D)/build/sway/sway         $(TARGET_DIR)/usr/bin
    $(INSTALL) -D $(@D)/build/swaymsg/swaymsg   $(TARGET_DIR)/usr/bin

    mkdir -p $(TARGET_DIR)/etc/sway
    $(INSTALL) -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/display/sway/config/config \
        $(TARGET_DIR)/etc/sway

    mkdir -p $(TARGET_DIR)/etc/profile.d
    $(INSTALL) -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/display/sway/config/04-sway.sh \
        $(TARGET_DIR)/etc/profile.d/04-sway.sh

    mkdir -p $(TARGET_DIR)/usr/bin
    $(INSTALL) -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/display/sway/config/sway-launch \
        $(TARGET_DIR)/usr/bin
endef

$(eval $(meson-package))
