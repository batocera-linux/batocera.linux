################################################################################
#
# kodi-pvr-vuplus
#
################################################################################

KODI18_PVR_VUPLUS_VERSION = 3.28.9-Leia
KODI18_PVR_VUPLUS_SITE = $(call github,kodi-pvr,pvr.vuplus,$(KODI18_PVR_VUPLUS_VERSION))
KODI18_PVR_VUPLUS_LICENSE = GPL-2.0+
KODI18_PVR_VUPLUS_LICENSE_FILES = debian/copyright
KODI18_PVR_VUPLUS_DEPENDENCIES = json-for-modern-cpp kodi18-platform tinyxml

$(eval $(cmake-package))
