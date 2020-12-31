################################################################################
#
# L3AFPAD
#
################################################################################

L3AFPAD_VERSION = v0.8.18.1.11
L3AFPAD_SITE = $(call github,stevenhoneyman,l3afpad,$(L3AFPAD_VERSION))

L3AFPAD_DEPENDENCIES = libgtk3 host-intltool
L3AFPAD_LICENSE = GPL-2.0+
L3AFPAD_LICENSE_FILES = COPYING

L3AFPAD_AUTORECONF = YES

$(eval $(autotools-package))
