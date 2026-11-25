################################################################################
#
# gamescope
#
################################################################################

GAMESCOPE_VERSION = 3.17.0
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES = YES
GAMESCOPE_LICENSE = BSD-2-Clause
GAMESCOPE_LICENSE_FILES = LICENSE

ifeq ($(BR2_PACKAGE_GAMESCOPE_WSI_LAYER_ONLY),y)
GAMESCOPE_DEPENDENCIES = glm stb vulkan-headers vulkan-loader wayland
GAMESCOPE_DEPENDENCIES += wayland-protocols xlib_libX11

GAMESCOPE_CONF_OPTS = \
	-Denable_gamescope=false \
	-Denable_gamescope_wsi_layer=true \
	-Dpipewire=disabled \
	-Denable_openvr_support=false \
	-Denable_zenity=false \
	-Denable_tests=false
else
GAMESCOPE_DEPENDENCIES = host-glslang glm hwdata libcap libdecor libdisplay-info
GAMESCOPE_DEPENDENCIES += batocera-luajit libinput libxkbcommon pixman stb udev
GAMESCOPE_DEPENDENCIES += vulkan-headers vulkan-loader wayland wayland-protocols
GAMESCOPE_DEPENDENCIES += wlroots xwayland xlib_libX11 xlib_libXcomposite
GAMESCOPE_DEPENDENCIES += xlib_libXcursor xlib_libXdamage xlib_libXext
GAMESCOPE_DEPENDENCIES += xlib_libXfixes xlib_libXi xlib_libXmu xlib_libXrender
GAMESCOPE_DEPENDENCIES += xlib_libXres xlib_libXtst xlib_libXxf86vm

# vkroots is header-only and gamescope refuses to build without its own copy
GAMESCOPE_CONF_OPTS = \
	-Ddrm_backend=disabled \
	-Dsdl2_backend=disabled \
	-Dpipewire=disabled \
	-Davif_screenshots=disabled \
	-Dinput_emulation=disabled \
	-Drt_cap=enabled \
	-Denable_openvr_support=false \
	-Denable_zenity=false \
	-Denable_tests=false \
	-Dbenchmark=disabled

# the control center changes the running game's settings through it
define GAMESCOPE_INSTALL_CONTROL_SCRIPT
	$(INSTALL) -D -m 0755 $(GAMESCOPE_PKGDIR)/batocera-gamescope $(TARGET_DIR)/usr/bin/batocera-gamescope
endef
GAMESCOPE_POST_INSTALL_TARGET_HOOKS += GAMESCOPE_INSTALL_CONTROL_SCRIPT
endif

$(eval $(call register,gamescope._shared.emulator.yml gamescope._emulators.emulator.yml))

$(eval $(meson-package))
$(eval $(emulator-info-package))
