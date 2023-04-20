################################################################################
#
# kodi20-audiodecoder-sidplay
#
################################################################################

KODI20_AUDIODECODER_SIDPLAY_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_SIDPLAY_SITE = $(call github,xbmc,audiodecoder.sidplay,$(KODI20_AUDIODECODER_SIDPLAY_VERSION))
KODI20_AUDIODECODER_SIDPLAY_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_SIDPLAY_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_SIDPLAY_DEPENDENCIES = host-pkgconf kodi20 libsidplay2

$(eval $(cmake-package))
