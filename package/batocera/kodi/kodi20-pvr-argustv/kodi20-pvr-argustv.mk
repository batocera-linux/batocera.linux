################################################################################
#
# kodi20-pvr-argustv
#
################################################################################

KODI20_PVR_ARGUSTV_VERSION = 20.5.0-Nexus
KODI20_PVR_ARGUSTV_SITE = $(call github,kodi-pvr,pvr.argustv,$(KODI20_PVR_ARGUSTV_VERSION))
KODI20_PVR_ARGUSTV_LICENSE = GPL-2.0+
KODI20_PVR_ARGUSTV_LICENSE_FILES = LICENSE.md
KODI20_PVR_ARGUSTV_DEPENDENCIES = jsoncpp kodi20

$(eval $(cmake-package))
