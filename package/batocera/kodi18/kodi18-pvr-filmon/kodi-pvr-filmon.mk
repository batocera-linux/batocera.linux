################################################################################
#
# kodi-pvr-filmon
#
################################################################################

KODI18_PVR_FILMON_VERSION = 2.4.4-Leia
KODI18_PVR_FILMON_SITE = $(call github,kodi-pvr,pvr.filmon,$(KODI18_PVR_FILMON_VERSION))
KODI18_PVR_FILMON_LICENSE = GPL-2.0+
KODI18_PVR_FILMON_LICENSE_FILES = debian/copyright
KODI18_PVR_FILMON_DEPENDENCIES = jsoncpp kodi18-platform

$(eval $(cmake-package))
