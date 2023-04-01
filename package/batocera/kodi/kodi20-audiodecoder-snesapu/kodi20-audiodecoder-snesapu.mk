################################################################################
#
# kodi20-audiodecoder-snesapu
#
################################################################################

KODI20_AUDIODECODER_SNESAPU_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_SNESAPU_SITE = $(call github,xbmc,audiodecoder.snesapu,$(KODI20_AUDIODECODER_SNESAPU_VERSION))
KODI20_AUDIODECODER_SNESAPU_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_SNESAPU_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_SNESAPU_DEPENDENCIES = kodi20

$(eval $(cmake-package))
