################################################################################
#
# kodi20-pvr-vuplus
#
################################################################################

KODI20_PVR_VUPLUS_VERSION = 20.5.1-Nexus
KODI20_PVR_VUPLUS_SITE = $(call github,kodi-pvr,pvr.vuplus,$(KODI20_PVR_VUPLUS_VERSION))
KODI20_PVR_VUPLUS_LICENSE = GPL-2.0+
KODI20_PVR_VUPLUS_LICENSE_FILES = LICENSE.md
KODI20_PVR_VUPLUS_DEPENDENCIES = json-for-modern-cpp kodi20 tinyxml

$(eval $(cmake-package))
