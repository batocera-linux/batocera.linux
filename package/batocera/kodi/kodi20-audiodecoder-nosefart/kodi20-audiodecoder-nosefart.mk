################################################################################
#
# kodi20-audiodecoder-nosefart
#
################################################################################

KODI20_AUDIODECODER_NOSEFART_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_NOSEFART_SITE = $(call github,xbmc,audiodecoder.nosefart,$(KODI20_AUDIODECODER_NOSEFART_VERSION))
KODI20_AUDIODECODER_NOSEFART_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_NOSEFART_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_NOSEFART_DEPENDENCIES = kodi20

$(eval $(cmake-package))
