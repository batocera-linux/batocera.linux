################################################################################
#
# kodi20-audioencoder-flac
#
################################################################################

KODI20_AUDIOENCODER_FLAC_VERSION = 20.2.0-Nexus
KODI20_AUDIOENCODER_FLAC_SITE = $(call github,xbmc,audioencoder.flac,$(KODI20_AUDIOENCODER_FLAC_VERSION))
KODI20_AUDIOENCODER_FLAC_LICENSE = GPL-2.0+
KODI20_AUDIOENCODER_FLAC_LICENSE_FILES = LICENSE.md
KODI20_AUDIOENCODER_FLAC_DEPENDENCIES = flac kodi20 libogg host-pkgconf

$(eval $(cmake-package))
