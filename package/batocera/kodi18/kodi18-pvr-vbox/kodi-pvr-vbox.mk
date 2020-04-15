################################################################################
#
# kodi-pvr-vbox
#
################################################################################

KODI18_PVR_VBOX_VERSION = 4.7.0-Leia
KODI18_PVR_VBOX_SITE = $(call github,kodi-pvr,pvr.vbox,$(KODI18_PVR_VBOX_VERSION))
KODI18_PVR_VBOX_LICENSE = GPL-2.0+
KODI18_PVR_VBOX_LICENSE_FILES = debian/copyright
KODI18_PVR_VBOX_DEPENDENCIES = kodi18-platform

$(eval $(cmake-package))
