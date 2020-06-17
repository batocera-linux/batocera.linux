################################################################################
#
# kodi-pvr-nextpvr
#
################################################################################

KODI18_PVR_NEXTPVR_VERSION = 3.3.19-Leia
KODI18_PVR_NEXTPVR_SITE = $(call github,kodi-pvr,pvr.nextpvr,$(KODI18_PVR_NEXTPVR_VERSION))
KODI18_PVR_NEXTPVR_LICENSE = GPL-2.0+
KODI18_PVR_NEXTPVR_LICENSE_FILES = debian/copyright
KODI18_PVR_NEXTPVR_DEPENDENCIES = kodi18-platform

$(eval $(cmake-package))
