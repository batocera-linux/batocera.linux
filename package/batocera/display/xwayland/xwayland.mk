################################################################################
#
# xwayland
#
################################################################################

XWAYLAND_VERSION = 22.1.4
XWAYLAND_SOURCE = xwayland-$(XWAYLAND_VERSION).tar.xz
XWAYLAND_SITE = https://www.x.org/releases/individual/xserver
XWAYLAND_LICENSE = MIT
XWAYLAND_LICENSE_FILES = COPYING
XWAYLAND_INSTALL_STAGING = YES

XWAYLAND_DEPENDENCIES = xorgproto pixman xlib_xtrans xlib_libxkbfile \
                        xlib_libXfont2 dbus wayland wayland-protocols waylandpp \
                        libdrm libepoxy xfont_font-util xapp_xkbcomp mesa3d \
                        xlib_libxcvt

XWAYLAND_CONF_OPTS += -Dxvfb=false -Ddocs=false -Ddri3=auto -Dxwayland-path=/usr/bin
XWAYLAND_CONF_OPTS += -Dxkb_dir=/usr/share/X11/xkb -Dxkb_output_dir=/var/lib/xkb
XWAYLAND_CONF_OPTS += -Dxwayland_eglstream=auto -Dglamor=true

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    XWAYLAND_CONF_OPTS += -Dglx=true
else
    XWAYLAND_CONF_OPTS += -Dglx=false
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    XWAYLAND_CONF_OPTS += -Ddrm=true
else
    XWAYLAND_CONF_OPTS += -Ddrm=false
endif

define XWAYLAND_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    $(INSTALL) -m755 -D $(@D)/build/hw/xwayland/Xwayland $(TARGET_DIR)/usr/bin
    $(INSTALL) -m644 -D $(@D)/build/hw/xwayland/xwayland.pc $(TARGET_DIR)/usr/lib/pkgconfig
endef

$(eval $(meson-package))
