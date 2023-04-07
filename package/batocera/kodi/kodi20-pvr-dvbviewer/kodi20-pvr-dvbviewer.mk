################################################################################
#
# kodi20-pvr-dvbviewer
#
################################################################################

KODI20_PVR_DVBVIEWER_VERSION = 20.4.0-Nexus
KODI20_PVR_DVBVIEWER_SITE = $(call github,kodi-pvr,pvr.dvbviewer,$(KODI20_PVR_DVBVIEWER_VERSION))
KODI20_PVR_DVBVIEWER_LICENSE = GPL-2.0+
KODI20_PVR_DVBVIEWER_LICENSE_FILES = LICENSE.md
KODI20_PVR_DVBVIEWER_DEPENDENCIES = kodi20 tinyxml

$(eval $(cmake-package))
