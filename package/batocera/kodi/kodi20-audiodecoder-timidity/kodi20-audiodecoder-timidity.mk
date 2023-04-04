################################################################################
#
# kodi20-audiodecoder-timidity
#
################################################################################

KODI20_AUDIODECODER_TIMIDITY_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_TIMIDITY_SITE = $(call github,xbmc,audiodecoder.timidity,$(KODI20_AUDIODECODER_TIMIDITY_VERSION))
KODI20_AUDIODECODER_TIMIDITY_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_TIMIDITY_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_TIMIDITY_DEPENDENCIES = kodi20

$(eval $(cmake-package))
