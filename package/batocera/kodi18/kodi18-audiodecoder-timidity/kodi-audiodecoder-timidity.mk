################################################################################
#
# kodi-audiodecoder-timidity
#
################################################################################

KODI18_AUDIODECODER_TIMIDITY_VERSION = 2.0.4-Leia
KODI18_AUDIODECODER_TIMIDITY_SITE = $(call github,xbmc,audiodecoder.timidity,$(KODI18_AUDIODECODER_TIMIDITY_VERSION))
KODI18_AUDIODECODER_TIMIDITY_LICENSE = GPL-2.0+
KODI18_AUDIODECODER_TIMIDITY_LICENSE_FILES = debian/copyright
KODI18_AUDIODECODER_TIMIDITY_DEPENDENCIES = kodi18

$(eval $(cmake-package))
