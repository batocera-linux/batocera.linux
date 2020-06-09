################################################################################
#
# kodi-pvr-argustv
#
################################################################################

KODI18_PVR_ARGUSTV_VERSION = 3.5.6-Leia
KODI18_PVR_ARGUSTV_SITE = $(call github,kodi-pvr,pvr.argustv,$(KODI18_PVR_ARGUSTV_VERSION))
KODI18_PVR_ARGUSTV_LICENSE = GPL-2.0+
KODI18_PVR_ARGUSTV_LICENSE_FILES = debian/copyright
KODI18_PVR_ARGUSTV_DEPENDENCIES = jsoncpp kodi18-platform

$(eval $(cmake-package))
