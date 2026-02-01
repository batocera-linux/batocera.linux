################################################################################
#
# gamescope
#
################################################################################

GAMESCOPE_VERSION = 3.16.4
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES=YES
GAMESCOPE_DEPENDENCIES = sdl2 libdrm wayland wayland-protocols glm hwdata pipewire xlib_libXres  xlib_libXmu stb seatd xwayland libdecor
GAMESCOPE_CONF_OPTS += -Denable_openvr_support=FALSE

define GAMESCOPE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/build/src/gamescope $(TARGET_DIR)/usr/bin/gamescope
endef

$(eval $(meson-package))
