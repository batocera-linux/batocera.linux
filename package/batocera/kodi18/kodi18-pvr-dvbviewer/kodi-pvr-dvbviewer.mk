################################################################################
#
# kodi-pvr-dvbviewer
#
################################################################################

KODI18_PVR_DVBVIEWER_VERSION = 3.7.11-Leia
KODI18_PVR_DVBVIEWER_SITE = $(call github,kodi-pvr,pvr.dvbviewer,$(KODI18_PVR_DVBVIEWER_VERSION))
KODI18_PVR_DVBVIEWER_LICENSE = GPL-2.0+
KODI18_PVR_DVBVIEWER_LICENSE_FILES = debian/copyright
KODI18_PVR_DVBVIEWER_DEPENDENCIES = kodi18-platform

$(eval $(cmake-package))
