################################################################################
#
# kodi-pvr-freebox
#
################################################################################

KODI_PVR_FREEBOX_VERSION = 6.1.4-Matrix
KODI_PVR_FREEBOX_SITE = $(call github,aassif,pvr.freebox,$(KODI_PVR_FREEBOX_VERSION))
KODI_PVR_FREEBOX_LICENSE = MIT
KODI_PVR_FREEBOX_DEPENDENCIES = kodi

$(eval $(cmake-package))
