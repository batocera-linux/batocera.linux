################################################################################
#
# kodi20-pvr-mediaportal-tvserver
#
################################################################################

KODI20_PVR_MEDIAPORTAL_TVSERVER_VERSION = 20.3.0-Nexus
KODI20_PVR_MEDIAPORTAL_TVSERVER_SITE = $(call github,kodi-pvr,pvr.mediaportal.tvserver,$(KODI20_PVR_MEDIAPORTAL_TVSERVER_VERSION))
KODI20_PVR_MEDIAPORTAL_TVSERVER_LICENSE = GPL-2.0+
KODI20_PVR_MEDIAPORTAL_TVSERVER_LICENSE_FILES = LICENSE.md
KODI20_PVR_MEDIAPORTAL_TVSERVER_DEPENDENCIES = kodi20 tinyxml

$(eval $(cmake-package))
