################################################################################
#
# kodi20-audioencoder-wav
#
################################################################################

KODI20_AUDIOENCODER_WAV_VERSION = 20.2.0-Nexus
KODI20_AUDIOENCODER_WAV_SITE = $(call github,xbmc,audioencoder.wav,$(KODI20_AUDIOENCODER_WAV_VERSION))
KODI20_AUDIOENCODER_WAV_LICENSE = GPL-2.0+
KODI20_AUDIOENCODER_WAV_LICENSE_FILES = LICENSE.md
KODI20_AUDIOENCODER_WAV_DEPENDENCIES = kodi20

$(eval $(cmake-package))
