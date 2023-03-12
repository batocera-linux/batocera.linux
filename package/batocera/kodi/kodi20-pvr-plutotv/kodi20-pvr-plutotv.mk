################################################################################
#
# kodi20-pvr-plutotv
#
################################################################################

KODI20_PVR_PLUTOTV_VERSION = 20.3.0-Nexus
KODI20_PVR_PLUTOTV_SITE = $(call github,kodi-pvr,pvr.plutotv,$(KODI20_PVR_PLUTOTV_VERSION))
KODI20_PVR_PLUTOTV_LICENSE = GPL-2.0+
KODI20_PVR_PLUTOTV_LICENSE_FILES = LICENSE.md
KODI20_PVR_PLUTOTV_DEPENDENCIES = kodi20 rapidjson

$(eval $(cmake-package))
