################################################################################
#
# kodi20-pvr-nextpvr
#
################################################################################

KODI20_PVR_NEXTPVR_VERSION = 20.4.2-Nexus
KODI20_PVR_NEXTPVR_SITE = $(call github,kodi-pvr,pvr.nextpvr,$(KODI20_PVR_NEXTPVR_VERSION))
KODI20_PVR_NEXTPVR_LICENSE = GPL-2.0+
KODI20_PVR_NEXTPVR_LICENSE_FILES = LICENSE.md
KODI20_PVR_NEXTPVR_DEPENDENCIES = kodi20 tinyxml2

$(eval $(cmake-package))
