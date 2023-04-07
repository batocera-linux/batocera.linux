################################################################################
#
# kodi20-pvr-waipu
#
################################################################################

KODI20_PVR_WAIPU_VERSION = 20.7.0-Nexus
KODI20_PVR_WAIPU_SITE = $(call github,flubshi,pvr.waipu,$(KODI20_PVR_WAIPU_VERSION))
KODI20_PVR_WAIPU_LICENSE = GPL-2.0+
KODI20_PVR_WAIPU_LICENSE_FILES = pvr.waipu/LICENSE.txt
KODI20_PVR_WAIPU_DEPENDENCIES = kodi20 rapidjson

$(eval $(cmake-package))
