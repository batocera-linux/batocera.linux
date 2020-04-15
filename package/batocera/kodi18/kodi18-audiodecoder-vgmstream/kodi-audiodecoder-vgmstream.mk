################################################################################
#
# kodi-audiodecoder-vgmstream
#
################################################################################

KODI18_AUDIODECODER_VGMSTREAM_VERSION = 1.1.5-Leia
KODI18_AUDIODECODER_VGMSTREAM_SITE = $(call github,xbmc,audiodecoder.vgmstream,$(KODI18_AUDIODECODER_VGMSTREAM_VERSION))
KODI18_AUDIODECODER_VGMSTREAM_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_VGMSTREAM_LICENSE_FILES = debian/copyright
KODI18_AUDIODECODER_VGMSTREAM_DEPENDENCIES = kodi18

$(eval $(cmake-package))
