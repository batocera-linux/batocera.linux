################################################################################
#
# kodi20-pvr-njoy
#
################################################################################

KODI20_PVR_NJOY_VERSION = 20.3.0-Nexus
KODI20_PVR_NJOY_SITE = $(call github,kodi-pvr,pvr.njoy,$(KODI20_PVR_NJOY_VERSION))
KODI20_PVR_NJOY_LICENSE = GPL-2.0+
KODI20_PVR_NJOY_LICENSE_FILES = LICENSE.md
KODI20_PVR_NJOY_DEPENDENCIES = kodi20 tinyxml

$(eval $(cmake-package))
