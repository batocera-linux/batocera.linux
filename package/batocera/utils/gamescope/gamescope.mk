################################################################################
#
# gamescope
#
################################################################################

GAMESCOPE_VERSION = 3.16.17
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES=YES

GAMESCOPE_DEPENDENCIES = sdl2 glm stb libdrm pipewire xlib_libXres xlib_libXmu libdecor luajit
GAMESCOPE_DEPENDENCIES += host-pkgconf host-wayland hwdata libdisplay-info libinput libxkbcommon libegl libgles libgbm pixman seatd udev wayland wayland-protocols libxcb xcb-util-wm xwayland


GAMESCOPE_CONF_OPTS = --wrap-mode=default
GAMESCOPE_CONF_OPTS += -Dpipewire=enabled
GAMESCOPE_CONF_OPTS += -Dwerror=false
GAMESCOPE_CONF_OPTS += -Denable_openvr_support=FALSE

ifeq ($(BR2_PACKAGE_LIBAVIF),y)
GAMESCOPE_DEPENDENCIES += libavif
GAMESCOPE_CONF_OPTS += -Davif_screenshots=enabled
else
GAMESCOPE_CONF_OPTS += -Davif_screenshots=disabled
endif

ifeq ($(BR2_PACKAGE_OPENVR),y)
GAMESCOPE_DEPENDENCIES += openvr
GAMESCOPE_CONF_OPTS += -Denable_openvr_support=TRUE
else
GAMESCOPE_CONF_OPTS += -Denable_openvr_support=FALSE
endif

ifeq ($(BR2_PACKAGE_LIBEI),y)
GAMESCOPE_DEPENDENCIES += libeis
GAMESCOPE_CONF_OPTS += -Dinput_emulation=enabled
else
GAMESCOPE_CONF_OPTS += -Dinput_emulation=disabled
endif

define GAMESCOPE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/build/src/gamescope $(TARGET_DIR)/usr/bin/gamescope
	$(INSTALL) -D $(@D)/build/src/gamescopereaper $(TARGET_DIR)/usr/bin/gamescopereaper
	$(INSTALL) -D $(@D)/build/src/gamescopestream $(TARGET_DIR)/usr/bin/gamescopestream
	$(INSTALL) -D $(@D)/build/src/gamescopectl $(TARGET_DIR)/usr/bin/gamescopectl
endef

$(eval $(meson-package))
