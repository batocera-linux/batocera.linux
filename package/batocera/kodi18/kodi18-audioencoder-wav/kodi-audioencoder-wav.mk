################################################################################
#
# kodi-audioencoder-wav
#
################################################################################

KODI18_AUDIOENCODER_WAV_VERSION = 2.0.2-Leia
KODI18_AUDIOENCODER_WAV_SITE = $(call github,xbmc,audioencoder.wav,$(KODI18_AUDIOENCODER_WAV_VERSION))
KODI18_AUDIOENCODER_WAV_LICENSE = GPL-2.0+
KODI18_AUDIOENCODER_WAV_LICENSE_FILES = src/EncoderWav.cpp
KODI18_AUDIOENCODER_WAV_DEPENDENCIES = kodi18

$(eval $(cmake-package))
