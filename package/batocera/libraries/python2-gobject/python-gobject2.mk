################################################################################
#
# python-gobject
#
################################################################################

PYTHON2_GOBJECT_VERSION_MAJOR = 2.28
PYTHON2_GOBJECT_VERSION = $(PYTHON2_GOBJECT_VERSION_MAJOR).6
PYTHON2_GOBJECT_SOURCE = pygobject-$(PYTHON2_GOBJECT_VERSION).tar.xz
PYTHON2_GOBJECT_SITE = http://ftp.gnome.org/pub/gnome/sources/pygobject/$(PYTHON2_GOBJECT_VERSION_MAJOR)
PYTHON2_GOBJECT_LICENSE = LGPL-2.1+
PYTHON2_GOBJECT_LICENSE_FILES = COPYING
PYTHON2_GOBJECT_DEPENDENCIES = host-pkgconf libglib2
PYTHON2_GOBJECT_CONF_OPTS = --disable-introspection
# for 0001-add-PYTHON_INCLUDES-override.patch
PYTHON2_GOBJECT_AUTORECONF = YES

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON2_GOBJECT_DEPENDENCIES += python host-python

PYTHON2_GOBJECT_CONF_ENV = \
	PYTHON=$(HOST_DIR)/bin/python2 \
	PYTHON_INCLUDES="`$(STAGING_DIR)/usr/bin/python2-config --includes`"
else
PYTHON2_GOBJECT_DEPENDENCIES += python3 host-python3

PYTHON2_GOBJECT_CONF_ENV = \
	PYTHON=$(HOST_DIR)/bin/python3 \
	PYTHON_INCLUDES="`$(STAGING_DIR)/usr/bin/python3-config --includes`"
endif

ifeq ($(BR2_PACKAGE_LIBFFI),y)
PYTHON2_GOBJECT_CONF_OPTS += --with-ffi
PYTHON2_GOBJECT_DEPENDENCIES += libffi
else
PYTHON2_GOBJECT_CONF_OPTS += --without-ffi
endif

$(eval $(autotools-package))
