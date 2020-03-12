################################################################################
#
# kodi-pvr-mediaportal-tvserver
#
################################################################################

KODI18_PVR_MEDIAPORTAL_TVSERVER_VERSION = 3.5.18-Leia
KODI18_PVR_MEDIAPORTAL_TVSERVER_SITE = $(call github,kodi-pvr,pvr.mediaportal.tvserver,$(KODI18_PVR_MEDIAPORTAL_TVSERVER_VERSION))
KODI18_PVR_MEDIAPORTAL_TVSERVER_LICENSE = GPL-2.0+
KODI18_PVR_MEDIAPORTAL_TVSERVER_LICENSE_FILES = debian/copyright
KODI18_PVR_MEDIAPORTAL_TVSERVER_DEPENDENCIES = kodi18-platform

$(eval $(cmake-package))
