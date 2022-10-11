################################################################################
#
# appstream-glib
#
################################################################################
APPSTREAM_GLIB_VERSION = appstream_glib_0_8_1
APPSTREAM_GLIB_SITE = $(call github,hughsie,appstream-glib,$(APPSTREAM_GLIB_VERSION))
APPSTREAM_GLIB_INSTALL_STAGING = YES

APPSTREAM_GLIB_DEPENDENCIES = libgtk3 libyaml json-glib

APPSTREAM_GLIB_CONF_OPTS = -Dstemmer=false -Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false -Drpm=false

$(eval $(meson-package))
