################################################################################
#
# kodi20-pvr-octonet
#
################################################################################

KODI20_PVR_OCTONET_VERSION = 20.3.0-Nexus
KODI20_PVR_OCTONET_SITE = $(call github,DigitalDevices,pvr.octonet,$(KODI20_PVR_OCTONET_VERSION))
KODI20_PVR_OCTONET_LICENSE = GPL-2.0+
KODI20_PVR_OCTONET_LICENSE_FILES = LICENSE.md
KODI20_PVR_OCTONET_DEPENDENCIES = jsoncpp kodi20

$(eval $(cmake-package))
