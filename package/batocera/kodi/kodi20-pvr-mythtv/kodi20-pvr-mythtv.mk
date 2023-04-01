################################################################################
#
# kodi20-pvr-mythtv
#
################################################################################

KODI20_PVR_MYTHTV_VERSION = 20.3.2-Nexus
KODI20_PVR_MYTHTV_SITE = $(call github,janbar,pvr.mythtv,$(KODI20_PVR_MYTHTV_VERSION))
KODI20_PVR_MYTHTV_LICENSE = GPL-2.0+
KODI20_PVR_MYTHTV_LICENSE_FILES = LICENSE.md
KODI20_PVR_MYTHTV_DEPENDENCIES = kodi20

$(eval $(cmake-package))
