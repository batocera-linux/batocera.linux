################################################################################
#
# kodi20-pvr-iptvsimple
#
################################################################################

KODI20_PVR_IPTVSIMPLE_VERSION = 20.10.1-Nexus
KODI20_PVR_IPTVSIMPLE_SITE = $(call github,kodi-pvr,pvr.iptvsimple,$(KODI20_PVR_IPTVSIMPLE_VERSION))
KODI20_PVR_IPTVSIMPLE_LICENSE = GPL-2.0+
KODI20_PVR_IPTVSIMPLE_LICENSE_FILES = LICENSE.md
KODI20_PVR_IPTVSIMPLE_DEPENDENCIES = kodi20 pugixml xz zlib

$(eval $(cmake-package))
