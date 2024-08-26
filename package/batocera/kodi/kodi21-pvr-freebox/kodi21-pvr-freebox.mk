################################################################################
#
# kodi21-pvr-freebox
#
################################################################################

KODI21_PVR_FREEBOX_VERSION = 21.0.0-Omega
KODI21_PVR_FREEBOX_SITE = $(call github,aassif,pvr.freebox,$(KODI21_PVR_FREEBOX_VERSION))
KODI21_PVR_FREEBOX_LICENSE = MIT
KODI21_PVR_FREEBOX_DEPENDENCIES = kodi

$(eval $(cmake-package))
