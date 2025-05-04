################################################################################
#
# labwc
#
################################################################################

LABWC_VERSION = 0.8.4
LABWC_SITE = $(call github,labwc,labwc,$(LABWC_VERSION))
LABWC_LICENSE = GPLv2
LABWC_LICENSE_FILES = LICENSE
LABWC_DEPENDENCIES = cairo host-pkgconf libglib2 libinput libpng libsfdo libxcb
LABWC_DEPENDENCIES += libxkbcommon libxml2 pango wayland wayland-protocols wlroots
LABWC_CONF_OPTS = \
	-Dman-pages=disabled \
	-Dstatic_analyzer=disabled \
	-Dtest=disabled

ifeq ($(BR2_PACKAGE_XWAYLAND),y)
LABWC_CONF_OPTS += -Dxwayland=enabled
LABWC_DEPENDENCIES += xwayland
else
LABWC_CONF_OPTS += -Dxwayland=disabled
endif

ifeq ($(BR2_PACKAGE_LIBRSVG),y)
LABWC_CONF_OPTS += -Dsvg=enabled
LABWC_DEPENDENCIES += librsvg
else
LABWC_CONF_OPTS += -Dsvg=disabled
endif

$(eval $(meson-package))
