################################################################################
#
# kodi20-pvr-pctv
#
################################################################################

KODI20_PVR_PCTV_VERSION = 20.4.0-Nexus
KODI20_PVR_PCTV_SITE = $(call github,kodi-pvr,pvr.pctv,$(KODI20_PVR_PCTV_VERSION))
KODI20_PVR_PCTV_LICENSE = GPL-2.0+
KODI20_PVR_PCTV_LICENSE_FILES = LICENSE.md
KODI20_PVR_PCTV_DEPENDENCIES = jsoncpp kodi20

$(eval $(cmake-package))
