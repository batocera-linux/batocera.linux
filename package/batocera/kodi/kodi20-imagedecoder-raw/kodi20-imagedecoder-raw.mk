################################################################################
#
# kodi20-imagedecoder-raw
#
################################################################################

KODI20_IMAGEDECODER_RAW_VERSION = 20.1.0-Nexus
KODI20_IMAGEDECODER_RAW_SITE = $(call github,xbmc,imagedecoder.raw,$(KODI20_IMAGEDECODER_RAW_VERSION))
KODI20_IMAGEDECODER_RAW_LICENSE = GPL-2.0+
KODI20_IMAGEDECODER_RAW_LICENSE_FILES = LICENSE.GPL
KODI20_IMAGEDECODER_RAW_DEPENDENCIES = kodi20 lcms2 jpeg-turbo libraw

KODI20_IMAGEDECODER_RAW_CONF_OPTS = -DADDONS_TO_BUILD=imagedecoder.raw

$(eval $(cmake-package))
