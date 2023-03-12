################################################################################
#
# kodi20-pvr-hdhomerun
#
################################################################################

KODI20_PVR_HDHOMERUN_VERSION = 20.4.0-Nexus
KODI20_PVR_HDHOMERUN_SITE = $(call github,kodi-pvr,pvr.hdhomerun,$(KODI20_PVR_HDHOMERUN_VERSION))
KODI20_PVR_HDHOMERUN_LICENSE = GPL-2.0+
KODI20_PVR_HDHOMERUN_LICENSE_FILES = LICENSE.md
KODI20_PVR_HDHOMERUN_DEPENDENCIES = jsoncpp kodi20 libhdhomerun

$(eval $(cmake-package))
