################################################################################
#
# kodi20-pvr-filmon
#
################################################################################

KODI20_PVR_FILMON_VERSION = 20.3.0-Nexus
KODI20_PVR_FILMON_SITE = $(call github,kodi-pvr,pvr.filmon,$(KODI20_PVR_FILMON_VERSION))
KODI20_PVR_FILMON_LICENSE = GPL-2.0+
KODI20_PVR_FILMON_LICENSE_FILES = LICENSE.md
KODI20_PVR_FILMON_DEPENDENCIES = jsoncpp kodi20

$(eval $(cmake-package))
