################################################################################
#
# kodi20-pvr-stalker
#
################################################################################

KODI20_PVR_STALKER_VERSION = 20.3.1-Nexus
KODI20_PVR_STALKER_SITE = $(call github,kodi-pvr,pvr.stalker,$(KODI20_PVR_STALKER_VERSION))
KODI20_PVR_STALKER_LICENSE = GPL-2.0+
KODI20_PVR_STALKER_LICENSE_FILES = LICENSE.md
KODI20_PVR_STALKER_DEPENDENCIES = jsoncpp kodi20 libxml2

$(eval $(cmake-package))
