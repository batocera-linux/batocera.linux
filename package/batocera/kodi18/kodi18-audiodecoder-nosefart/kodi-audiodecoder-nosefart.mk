################################################################################
#
# kodi-audiodecoder-nosefart
#
################################################################################

KODI18_AUDIODECODER_NOSEFART_VERSION = 2.0.2-Leia
KODI18_AUDIODECODER_NOSEFART_SITE = $(call github,xbmc,audiodecoder.nosefart,$(KODI18_AUDIODECODER_NOSEFART_VERSION))
KODI18_AUDIODECODER_NOSEFART_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_NOSEFART_LICENSE_FILES = debian/copyright
KODI18_AUDIODECODER_NOSEFART_DEPENDENCIES = kodi18

$(eval $(cmake-package))
