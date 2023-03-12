################################################################################
#
# kodi20-pvr-hts
#
################################################################################

KODI20_PVR_HTS_VERSION = 20.6.1-Nexus
KODI20_PVR_HTS_SITE = $(call github,kodi-pvr,pvr.hts,$(KODI20_PVR_HTS_VERSION))
KODI20_PVR_HTS_LICENSE = GPL-2.0+
KODI20_PVR_HTS_LICENSE_FILES = LICENSE.md
KODI20_PVR_HTS_DEPENDENCIES = kodi20

$(eval $(cmake-package))
