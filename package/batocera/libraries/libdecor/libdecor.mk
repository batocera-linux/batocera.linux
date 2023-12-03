################################################################################
#
# libdecor
#
################################################################################

LIBDECOR_VERSION = 0.2.1
LIBDECOR_SITE = https://gitlab.freedesktop.org/libdecor/libdecor/-/releases/$(LIBDECOR_VERSION)/downloads
LIBDECOR_SOURCE = libdecor-$(LIBDECOR_VERSION).tar.xz
LIBDECOR_LICENSE = MIT
LIBDECOR_LICENSE_FILES = LICENSE
LIBDECOR_INSTALL_STAGING = YES

LIBDECOR_DEPENDENCIES = \
	host-pkgconf \
	host-wayland \
	libxkbcommon \
	wayland \
	wayland-protocols \
	cairo \
	pango

LIBDECOR_CONF_OPTS = -Ddemo=false -Dgtk=disabled -Ddbus=enabled -Dinstall_demo=false

$(eval $(meson-package))
