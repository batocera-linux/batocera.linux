################################################################################
#
# kodi-audiodecoder-stsound
#
################################################################################

KODI18_AUDIODECODER_STSOUND_VERSION = 2.0.2-Leia
KODI18_AUDIODECODER_STSOUND_SITE = $(call github,xbmc,audiodecoder.stsound,$(KODI18_AUDIODECODER_STSOUND_VERSION))
KODI18_AUDIODECODER_STSOUND_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_STSOUND_LICENSE_FILES = debian/copyright
KODI18_AUDIODECODER_STSOUND_DEPENDENCIES = kodi18

$(eval $(cmake-package))
