################################################################################
#
# kodi20-pvr-wmc
#
################################################################################

KODI20_PVR_WMC_VERSION = 20.3.0-Nexus
KODI20_PVR_WMC_SITE = $(call github,kodi-pvr,pvr.wmc,$(KODI20_PVR_WMC_VERSION))
KODI20_PVR_WMC_LICENSE = GPL-2.0+
KODI20_PVR_WMC_LICENSE_FILES = LICENSE.md
KODI20_PVR_WMC_DEPENDENCIES = kodi20

$(eval $(cmake-package))
