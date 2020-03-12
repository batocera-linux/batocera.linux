################################################################################
#
# kodi-pvr-hdhomerun
#
################################################################################

KODI18_PVR_HDHOMERUN_VERSION = 3.5.0-Leia
KODI18_PVR_HDHOMERUN_SITE = $(call github,kodi-pvr,pvr.hdhomerun,$(KODI18_PVR_HDHOMERUN_VERSION))
KODI18_PVR_HDHOMERUN_LICENSE = GPL-2.0+
KODI18_PVR_HDHOMERUN_LICENSE_FILES = debian/copyright
KODI18_PVR_HDHOMERUN_DEPENDENCIES = jsoncpp kodi18-platform libhdhomerun

$(eval $(cmake-package))
