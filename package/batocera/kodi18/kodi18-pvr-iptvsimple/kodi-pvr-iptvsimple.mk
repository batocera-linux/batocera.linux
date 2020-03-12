################################################################################
#
# kodi-pvr-iptvsimple
#
################################################################################

KODI18_PVR_IPTVSIMPLE_VERSION = 3.9.8-Leia
KODI18_PVR_IPTVSIMPLE_SITE = $(call github,kodi-pvr,pvr.iptvsimple,$(KODI18_PVR_IPTVSIMPLE_VERSION))
KODI18_PVR_IPTVSIMPLE_LICENSE = GPL-2.0+
KODI18_PVR_IPTVSIMPLE_LICENSE_FILES = debian/copyright
KODI18_PVR_IPTVSIMPLE_DEPENDENCIES = kodi18-platform rapidxml

$(eval $(cmake-package))
