################################################################################
#
# kodi-audiodecoder-stsound
#
################################################################################

KODI18_AUDIODECODER_STSOUND_VERSION = 2.0.1-Leia
KODI18_AUDIODECODER_STSOUND_SITE = $(call github,xbmc,audiodecoder.stsound,$(KODI18_AUDIODECODER_STSOUND_VERSION))
KODI18_AUDIODECODER_STSOUND_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_STSOUND_LICENSE_FILES = src/YMCodec.cpp
KODI18_AUDIODECODER_STSOUND_DEPENDENCIES = kodi18

$(eval $(cmake-package))
