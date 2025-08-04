################################################################################
#
# picom
#
################################################################################

PICOM_VERSION = v12.5
PICOM_SITE = $(call github,yshui,picom,$(PICOM_VERSION))
PICOM_LICENSE = MPL-2.0 AND MIT
PICOM_LICENSE_FILES = LICENSE.spdx

PICOM_DEPENDENCIES += libconfig libev libxcb pixman uthash xcb-util 
PICOM_DEPENDENCIES += xcb-util-image xcb-util-renderutil xlib_libXcomposite
PICOM_DEPENDENCIES += xlib_libXdamage xlib_libXext xlib_libXfixes
PICOM_DEPENDENCIES += xlib_libXpresent xlib_libXrandr xlib_libXrender xorgproto

PICOM_CONF_OPTS += -Dsanitize=false
PICOM_CONF_OPTS += -Dxrescheck=false
PICOM_CONF_OPTS += -Dcompton=true
PICOM_CONF_OPTS += -Dwith_docs=false
PICOM_CONF_OPTS += -Dunittest=false
PICOM_CONF_OPTS += -Dmodularize=false
PICOM_CONF_OPTS += -Dllvm_coverage=false

ifeq ($(BR2_PACKAGE_DBUS),y)
PICOM_DEPENDENCIES += dbus
PICOM_CONF_OPTS += -Ddbus=true
else
PICOM_CONF_OPTS += -Ddbus=false
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
PICOM_DEPENDENCIES += libgl libepoxy libegl
PICOM_CONF_OPTS += -Dopengl=true
else
PICOM_CONF_OPTS += -Dopengl=false
endif

ifeq ($(BR2_PACKAGE_PCRE2),y)
PICOM_DEPENDENCIES += pcre2
PICOM_CONF_OPTS += -Dregex=true
else
PICOM_CONF_OPTS += -Dregex=false
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBX11),y)
PICOM_DEPENDENCIES += xlib_libX11
endif

define PICOM_CONFIG_FILE
    mkdir -p $(TARGET_DIR)/etc/xdg/picom
	cp -f $(PICOM_PKGDIR)/picom.conf $(TARGET_DIR)/etc/xdg/picom/
endef

PICOM_POST_INSTALL_TARGET_HOOKS = PICOM_CONFIG_FILE

$(eval $(meson-package))
