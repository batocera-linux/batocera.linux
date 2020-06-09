################################################################################
#
# kodi-pvr-mythtv
#
################################################################################

KODI18_PVR_MYTHTV_VERSION = 5.10.16-Leia
KODI18_PVR_MYTHTV_SITE = $(call github,janbar,pvr.mythtv,$(KODI18_PVR_MYTHTV_VERSION))
KODI18_PVR_MYTHTV_LICENSE = GPL-2.0+
KODI18_PVR_MYTHTV_LICENSE_FILES = debian/copyright
KODI18_PVR_MYTHTV_DEPENDENCIES = kodi18-platform

$(eval $(cmake-package))
