################################################################################
#
# kodi20-audioencoder-vorbis
#
################################################################################

KODI20_AUDIOENCODER_VORBIS_VERSION = 20.2.0-Nexus
KODI20_AUDIOENCODER_VORBIS_SITE = $(call github,xbmc,audioencoder.vorbis,$(KODI20_AUDIOENCODER_VORBIS_VERSION))
KODI20_AUDIOENCODER_VORBIS_LICENSE = GPL-2.0+
KODI20_AUDIOENCODER_VORBIS_LICENSE_FILES = LICENSE.md
KODI20_AUDIOENCODER_VORBIS_DEPENDENCIES = kodi20 libogg libvorbis host-pkgconf

$(eval $(cmake-package))
