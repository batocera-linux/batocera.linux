################################################################################
#
# kodi20-inputstream-adaptive
#
################################################################################

KODI20_INPUTSTREAM_ADAPTIVE_VERSION = 20.3.5-Nexus
KODI20_INPUTSTREAM_ADAPTIVE_SITE = $(call github,xbmc,inputstream.adaptive,$(KODI20_INPUTSTREAM_ADAPTIVE_VERSION))
KODI20_INPUTSTREAM_ADAPTIVE_LICENSE = GPL-2.0+
KODI20_INPUTSTREAM_ADAPTIVE_LICENSE_FILES = LICENSE.GPL
KODI20_INPUTSTREAM_ADAPTIVE_DEPENDENCIES = kodi20

KODI20_INPUTSTREAM_ADAPTIVE_CONF_OPTS = -DADDONS_TO_BUILD=inputstream.adaptive

$(eval $(cmake-package))
