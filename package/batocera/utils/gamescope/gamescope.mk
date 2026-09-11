################################################################################
#
# gamescope
#
################################################################################

GAMESCOPE_VERSION = 3.16.25
GAMESCOPE_SITE = https://github.com/ValveSoftware/gamescope
GAMESCOPE_SITE_METHOD = git
GAMESCOPE_GIT_SUBMODULES=YES

GAMESCOPE_DEPENDENCIES += host-glslang hwdata libdisplay-info libinput libxcb libxkbcommon
GAMESCOPE_DEPENDENCIES += pixman udev vulkan-headers vulkan-loader wayland wayland-protocols
GAMESCOPE_DEPENDENCIES += xcb-util-wm xwayland
GAMESCOPE_DEPENDENCIES += xlib_libX11 xlib_libXcomposite xlib_libXcursor xlib_libXdamage
GAMESCOPE_DEPENDENCIES += xlib_libXext xlib_libXfixes xlib_libXi xlib_libXmu xlib_libXrender
GAMESCOPE_DEPENDENCIES += xlib_libXres xlib_libXtst xlib_libXxf86vm

GAMESCOPE_CONF_OPTS = --wrap-mode=default
GAMESCOPE_CONF_OPTS += -Dbenchmark=disabled
GAMESCOPE_CONF_OPTS += -Denable_openvr_support=false
GAMESCOPE_CONF_OPTS += -Dinput_emulation=disabled
GAMESCOPE_CONF_OPTS += -Denable_tests=false

GAMESCOPE_FALLBACK_DEPS = wlroots,libliftoff,vkroots,luajit,libdecor-0,libseat

GAMESCOPE_CONF_OPTS += --force-fallback-for=$(GAMESCOPE_FALLBACK_DEPS)
GAMESCOPE_CONF_OPTS += -Dluajit:default_library=static
GAMESCOPE_CONF_OPTS += -Dluajit:luajit=false
GAMESCOPE_CONF_OPTS += -Dlibdecor:default_library=static
GAMESCOPE_CONF_OPTS += -Dlibdecor:dbus=disabled
GAMESCOPE_CONF_OPTS += -Dlibdecor:demo=false
GAMESCOPE_CONF_OPTS += -Dlibdecor:gtk=disabled

GAMESCOPE_CONF_OPTS += -Dseatd:default_library=static
GAMESCOPE_CONF_OPTS += -Dseatd:libseat-builtin=enabled
GAMESCOPE_CONF_OPTS += -Dseatd:libseat-logind=disabled
GAMESCOPE_CONF_OPTS += -Dseatd:man-pages=disabled
GAMESCOPE_CONF_OPTS += -Dseatd:server=disabled

GAMESCOPE_CONF_OPTS += -Dlibliftoff:werror=false
GAMESCOPE_CONF_OPTS += -Dseatd:werror=false
GAMESCOPE_CONF_OPTS += -Dwlroots:werror=false

GAMESCOPE_EXTRA_DOWNLOADS += https://gitlab.freedesktop.org/libdecor/libdecor/-/archive/0.2.1/libdecor-0.2.1.tar.gz
GAMESCOPE_EXTRA_DOWNLOADS += https://git.sr.ht/~kennylevinsen/seatd/archive/0.9.0.tar.gz
GAMESCOPE_EXTRA_DOWNLOADS += https://github.com/mesonbuild/wrapdb/releases/download/luajit_2.1.1720049189-3/luajit-2.1.1720049189.tar.gz
GAMESCOPE_EXTRA_DOWNLOADS += https://github.com/mesonbuild/wrapdb/releases/download/luajit_2.1.1720049189-3/luajit_2.1.1720049189-3_patch.zip

define GAMESCOPE_ADD_STATIC_SUBPROJECTS
	mkdir -p $(@D)/subprojects/packagefiles $(@D)/subprojects/packagecache
	cp -f $(GAMESCOPE_PKGDIR)/subprojects/*.wrap $(@D)/subprojects/
	cp -f $(GAMESCOPE_PKGDIR)/subprojects/packagefiles/* $(@D)/subprojects/packagefiles/
	cp -f $(GAMESCOPE_DL_DIR)/libdecor-0.2.1.tar.gz $(@D)/subprojects/packagecache/
	cp -f $(GAMESCOPE_DL_DIR)/0.9.0.tar.gz $(@D)/subprojects/packagecache/seatd-0.9.0.tar.gz
	cp -f $(GAMESCOPE_DL_DIR)/luajit-2.1.1720049189.tar.gz $(@D)/subprojects/packagecache/
	cp -f $(GAMESCOPE_DL_DIR)/luajit_2.1.1720049189-3_patch.zip $(@D)/subprojects/packagecache/
endef
GAMESCOPE_PRE_CONFIGURE_HOOKS += GAMESCOPE_ADD_STATIC_SUBPROJECTS

ifeq ($(BR2_PACKAGE_LIBAVIF),y)
GAMESCOPE_DEPENDENCIES += libavif
GAMESCOPE_CONF_OPTS += -Davif_screenshots=enabled
else
GAMESCOPE_CONF_OPTS += -Davif_screenshots=disabled
endif

ifeq ($(BR2_PACKAGE_LIBCAP),y)
GAMESCOPE_DEPENDENCIES += libcap
GAMESCOPE_CONF_OPTS += -Drt_cap=enabled
else
GAMESCOPE_CONF_OPTS += -Drt_cap=disabled
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
        $(INSTALL) -D $(@D)/buildroot-build/src/gamescope $(TARGET_DIR)/usr/bin/gamescope
        $(INSTALL) -D $(@D)/buildroot-build/src/gamescopereaper $(TARGET_DIR)/usr/bin/gamescopereaper
        $(INSTALL) -D $(@D)/buildroot-build/src/gamescopestream $(TARGET_DIR)/usr/bin/gamescopestream
        $(INSTALL) -D $(@D)/buildroot-build/src/gamescopectl $(TARGET_DIR)/usr/bin/gamescopectl

        mkdir -p $(TARGET_DIR)/usr/share/gamescope
        cp -dpfr $(@D)/scripts $(TARGET_DIR)/usr/share/gamescope/scripts
        cp -dpfr $(@D)/looks $(TARGET_DIR)/usr/share/gamescope/looks
endef

$(eval $(meson-package))
