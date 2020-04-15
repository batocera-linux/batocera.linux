################################################################################
#
# kodi-pvr-stalker
#
################################################################################

KODI18_PVR_STALKER_VERSION = 3.4.10-Leia
KODI18_PVR_STALKER_SITE = $(call github,kodi-pvr,pvr.stalker,$(KODI18_PVR_STALKER_VERSION))
KODI18_PVR_STALKER_LICENSE = GPL-2.0+
KODI18_PVR_STALKER_LICENSE_FILES = debian/copyright
KODI18_PVR_STALKER_DEPENDENCIES = jsoncpp kodi18-platform libxml2

$(eval $(cmake-package))
