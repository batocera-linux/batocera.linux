################################################################################
#
# LIBDISPLAY_INFO
#
################################################################################

LIBDISPLAY_INFO_VERSION = 0.1.1
LIBDISPLAY_INFO_SITE = https://gitlab.freedesktop.org/emersion/libdisplay-info/-/archive/$(LIBDISPLAY_INFO_VERSION)
LIBDISPLAY_INFO__SOURCE = libdisplay-info-$(LIBDISPLAY_INFO_VERSION).tar.gz
LIBDISPLAY_INFO_LICENSE = MIT
LIBDISPLAY_INFO_LICENSE_FILES = LICENSE
LIBDISPLAY_INFO_DEPENDENCIES = hwdata
LIBDISPLAY_INFO_INSTALL_STAGING = YES

$(eval $(meson-package))
