################################################################################
#
# kodi20-pvr-zattoo
#
################################################################################

KODI20_PVR_ZATTOO_VERSION = 20.3.6-Nexus
KODI20_PVR_ZATTOO_SITE = $(call github,rbuehlma,pvr.zattoo,$(KODI20_PVR_ZATTOO_VERSION))
KODI20_PVR_ZATTOO_LICENSE = GPL-2.0+
KODI20_PVR_ZATTOO_LICENSE_FILES = LICENSE.md
KODI20_PVR_ZATTOO_DEPENDENCIES = kodi20 rapidjson tinyxml2

$(eval $(cmake-package))
