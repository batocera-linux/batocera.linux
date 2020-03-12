################################################################################
#
# kodi-audiodecoder-sidplay
#
################################################################################

KODI18_AUDIODECODER_SIDPLAY_VERSION = 1.2.2-Leia
KODI18_AUDIODECODER_SIDPLAY_SITE = $(call github,xbmc,audiodecoder.sidplay,$(KODI18_AUDIODECODER_SIDPLAY_VERSION))
KODI18_AUDIODECODER_SIDPLAY_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_SIDPLAY_LICENSE_FILES = debian/copyright
KODI18_AUDIODECODER_SIDPLAY_DEPENDENCIES = host-pkgconf kodi18 libsidplay2

$(eval $(cmake-package))
