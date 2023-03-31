################################################################################
#
# kodi20-pvr-vbox
#
################################################################################

KODI20_PVR_VBOX_VERSION = 20.4.2-Nexus
KODI20_PVR_VBOX_SITE = $(call github,kodi-pvr,pvr.vbox,$(KODI20_PVR_VBOX_VERSION))
KODI20_PVR_VBOX_LICENSE = GPL-2.0+
KODI20_PVR_VBOX_LICENSE_FILES = LICENSE.md
KODI20_PVR_VBOX_DEPENDENCIES = kodi20

$(eval $(cmake-package))
