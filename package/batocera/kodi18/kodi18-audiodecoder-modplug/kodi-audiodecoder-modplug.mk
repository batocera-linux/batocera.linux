################################################################################
#
# kodi-audiodecoder-modplug
#
################################################################################

KODI18_AUDIODECODER_MODPLUG_VERSION = 2.0.2-Leia
KODI18_AUDIODECODER_MODPLUG_SITE = $(call github,xbmc,audiodecoder.modplug,$(KODI18_AUDIODECODER_MODPLUG_VERSION))
KODI18_AUDIODECODER_MODPLUG_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_MODPLUG_LICENSE_FILES = src/ModplugCodec.cpp
KODI18_AUDIODECODER_MODPLUG_DEPENDENCIES = kodi18 libmodplug

$(eval $(cmake-package))
