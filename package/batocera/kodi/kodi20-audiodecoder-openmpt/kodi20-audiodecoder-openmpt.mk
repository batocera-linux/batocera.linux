################################################################################
#
# kodi20-audiodecoder-openmpt
#
################################################################################

KODI20_AUDIODECODER_OPENMPT_VERSION = 20.2.0-Nexus
KODI20_AUDIODECODER_OPENMPT_SITE = $(call github,xbmc,audiodecoder.openmpt,$(KODI20_AUDIODECODER_OPENMPT_VERSION))
KODI20_AUDIODECODER_OPENMPT_LICENSE = GPL-2.0+
KODI20_AUDIODECODER_OPENMPT_LICENSE_FILES = LICENSE.md
KODI20_AUDIODECODER_OPENMPT_DEPENDENCIES = kodi20 zlib libopenmpt

$(eval $(cmake-package))
