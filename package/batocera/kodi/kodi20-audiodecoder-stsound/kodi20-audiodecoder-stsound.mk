################################################################################
#
# kodi20-audiodecoder-stsound
#
################################################################################

KODI20_AUDIODECODER_STSOUND_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_STSOUND_SITE = $(call github,xbmc,audiodecoder.stsound,$(KODI20_AUDIODECODER_STSOUND_VERSION))
KODI20_AUDIODECODER_STSOUND_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_STSOUND_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_STSOUND_DEPENDENCIES = kodi20

$(eval $(cmake-package))
