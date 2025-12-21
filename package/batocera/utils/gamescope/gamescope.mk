################################################################################
#
# gamescope
#
################################################################################

GAMESCOPE_VERSION = 3.16.17
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES=YES

GAMESCOPE_DEPENDENCIES += hwdata libdisplay-info libdecor luajit seatd
GAMESCOPE_DEPENDENCIES += vulkan-headers vulkan-loader wayland wayland-protocols
GAMESCOPE_DEPENDENCIES += xlib_libX11 xlib_libXmu xlib_libXres xwayland

GAMESCOPE_CONF_OPTS = --wrap-mode=default
GAMESCOPE_CONF_OPTS += -Dbenchmark=disabled
GAMESCOPE_CONF_OPTS += -Denable_openvr_support=false
GAMESCOPE_CONF_OPTS += -Dinput_emulation=disabled

ifeq ($(BR2_PACKAGE_LIBAVIF),y)
GAMESCOPE_DEPENDENCIES += libavif
GAMESCOPE_CONF_OPTS += -Davif_screenshots=enabled
else
GAMESCOPE_CONF_OPTS += -Davif_screenshots=disabled
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
GAMESCOPE_DEPENDENCIES += libdrm
GAMESCOPE_CONF_OPTS += -Ddrm_backend=enabled
else
GAMESCOPE_CONF_OPTS += -Ddrm_backend=disabled
endif

ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
GAMESCOPE_DEPENDENCIES += pipewire
GAMESCOPE_CONF_OPTS += -Dpipewire=enabled
else
GAMESCOPE_CONF_OPTS += -Dpipewire=disabled
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
GAMESCOPE_DEPENDENCIES += sdl2
GAMESCOPE_CONF_OPTS += -Dsdl2_backend=enabled
else
GAMESCOPE_CONF_OPTS += -Dsdl2_backend=disabled
endif

define GAMESCOPE_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        $(INSTALL) -D $(@D)/build/src/gamescope $(TARGET_DIR)/usr/bin/gamescope
        $(INSTALL) -D $(@D)/build/src/gamescopereaper $(TARGET_DIR)/usr/bin/gamescopereaper
        $(INSTALL) -D $(@D)/build/src/gamescopestream $(TARGET_DIR)/usr/bin/gamescopestream
        $(INSTALL) -D $(@D)/build/src/gamescopectl $(TARGET_DIR)/usr/bin/gamescopectl
endef

$(eval $(meson-package))
