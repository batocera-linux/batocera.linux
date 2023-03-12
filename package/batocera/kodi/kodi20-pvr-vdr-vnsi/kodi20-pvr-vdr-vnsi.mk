################################################################################
#
# kodi20-pvr-vdr-vnsi
#
################################################################################

KODI20_PVR_VDR_VNSI_VERSION = 20.4.0-Nexus
KODI20_PVR_VDR_VNSI_SITE = $(call github,kodi-pvr,pvr.vdr.vnsi,$(KODI20_PVR_VDR_VNSI_VERSION))
KODI20_PVR_VDR_VNSI_LICENSE = GPL-2.0+
KODI20_PVR_VDR_VNSI_LICENSE_FILES = LICENSE.md
KODI20_PVR_VDR_VNSI_DEPENDENCIES = kodi20

$(eval $(cmake-package))
