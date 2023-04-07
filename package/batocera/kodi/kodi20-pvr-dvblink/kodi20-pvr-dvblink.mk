################################################################################
#
# kodi20-pvr-dvblink
#
################################################################################

KODI20_PVR_DVBLINK_VERSION = 20.3.0-Nexus
KODI20_PVR_DVBLINK_SITE = $(call github,kodi-pvr,pvr.dvblink,$(KODI20_PVR_DVBLINK_VERSION))
KODI20_PVR_DVBLINK_LICENSE = GPL-2.0+
KODI20_PVR_DVBLINK_LICENSE_FILES = LICENSE.md
KODI20_PVR_DVBLINK_DEPENDENCIES = kodi20 tinyxml2

$(eval $(cmake-package))
