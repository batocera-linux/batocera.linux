################################################################################
#
# kodi-audioencoder-vorbis
#
################################################################################

KODI18_AUDIOENCODER_VORBIS_VERSION = 2.0.4-Leia
KODI18_AUDIOENCODER_VORBIS_SITE = $(call github,xbmc,audioencoder.vorbis,$(KODI18_AUDIOENCODER_VORBIS_VERSION))
KODI18_AUDIOENCODER_VORBIS_LICENSE = GPL-2.0+
KODI18_AUDIOENCODER_VORBIS_LICENSE_FILES = debian/copyright
KODI18_AUDIOENCODER_VORBIS_DEPENDENCIES = kodi18 libogg libvorbis host-pkgconf

$(eval $(cmake-package))
