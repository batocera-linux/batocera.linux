################################################################################
#
# kodi-pvr-dvblink
#
################################################################################

KODI18_PVR_DVBLINK_VERSION = 4.7.2-Leia
KODI18_PVR_DVBLINK_SITE = $(call github,kodi-pvr,pvr.dvblink,$(KODI18_PVR_DVBLINK_VERSION))
KODI18_PVR_DVBLINK_LICENSE = GPL-2.0+
KODI18_PVR_DVBLINK_LICENSE_FILES = debian/copyright
KODI18_PVR_DVBLINK_DEPENDENCIES = kodi18-platform tinyxml2

$(eval $(cmake-package))
