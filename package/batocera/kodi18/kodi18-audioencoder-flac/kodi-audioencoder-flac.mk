################################################################################
#
# kodi-audioencoder-flac
#
################################################################################

KODI18_AUDIOENCODER_FLAC_VERSION = 2.0.6-Leia
KODI18_AUDIOENCODER_FLAC_SITE = $(call github,xbmc,audioencoder.flac,$(KODI18_AUDIOENCODER_FLAC_VERSION))
KODI18_AUDIOENCODER_FLAC_LICENSE = GPL-2.0+
KODI18_AUDIOENCODER_FLAC_LICENSE_FILES = debian/copyright
KODI18_AUDIOENCODER_FLAC_DEPENDENCIES = flac kodi18 libogg host-pkgconf

$(eval $(cmake-package))
