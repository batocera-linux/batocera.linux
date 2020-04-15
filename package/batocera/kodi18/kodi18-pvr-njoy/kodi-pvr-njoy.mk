################################################################################
#
# kodi-pvr-njoy
#
################################################################################

KODI18_PVR_NJOY_VERSION = 3.4.2-Leia
KODI18_PVR_NJOY_SITE = $(call github,kodi-pvr,pvr.njoy,$(KODI18_PVR_NJOY_VERSION))
KODI18_PVR_NJOY_LICENSE = GPL-2.0+
KODI18_PVR_NJOY_LICENSE_FILES = debian/copyright
KODI18_PVR_NJOY_DEPENDENCIES = kodi18-platform

$(eval $(cmake-package))
