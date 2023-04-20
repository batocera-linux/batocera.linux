################################################################################
#
# kodi20-audiodecoder-vgmstream
#
################################################################################

KODI20_AUDIODECODER_VGMSTREAM_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_VGMSTREAM_SITE = $(call github,xbmc,audiodecoder.vgmstream,$(KODI20_AUDIODECODER_VGMSTREAM_VERSION))
KODI20_AUDIODECODER_VGMSTREAM_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_VGMSTREAM_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_VGMSTREAM_DEPENDENCIES = kodi20

$(eval $(cmake-package))
