################################################################################
#
# kodi-audiodecoder-modplug
#
################################################################################

KODI18_AUDIODECODER_MODPLUG_VERSION = 2.0.3-Leia
KODI18_AUDIODECODER_MODPLUG_SITE = $(call github,xbmc,audiodecoder.modplug,$(KODI18_AUDIODECODER_MODPLUG_VERSION))
KODI18_AUDIODECODER_MODPLUG_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_MODPLUG_LICENSE_FILES = debian/copyright
KODI18_AUDIODECODER_MODPLUG_DEPENDENCIES = kodi18 libmodplug

$(eval $(cmake-package))
