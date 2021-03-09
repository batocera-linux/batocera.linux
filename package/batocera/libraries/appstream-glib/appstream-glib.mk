################################################################################
#
# mali-g31-gbm
#
################################################################################
APPSTREAM_GLIB_VERSION = appstream_glib_0_7_18
APPSTREAM_GLIB_SITE = $(call github,hughsie,appstream-glib,$(APPSTREAM_GLIB_VERSION))
APPSTREAM_GLIB_INSTALL_STAGING = YES

APPSTREAM_GLIB_DEPENDENCIES = libgtk3 rpm libyaml json-glib

APPSTREAM_GLIB_CONF_OPTS = -Dstemmer=false -Dintrospection=false -Dbuilder=false -Dman=false -Dgtk-doc=false

$(eval $(meson-package))
