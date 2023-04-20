################################################################################
#
# kodi20-imagedecoder-raw
#
################################################################################

KODI20_IMAGEDECODER_HEIF_VERSION = 20.1.0-Nexus
KODI20_IMAGEDECODER_HEIF_SITE = $(call github,xbmc,imagedecoder.heif,$(KODI20_IMAGEDECODER_HEIF_VERSION))
KODI20_IMAGEDECODER_HEIF_LICENSE = GPL-2.0+
KODI20_IMAGEDECODER_HEIF_LICENSE_FILES = LICENSE.GPL
KODI20_IMAGEDECODER_HEIF_DEPENDENCIES = kodi20 libde265 libheif libxml2

KODI20_IMAGEDECODER_HEIF_CONF_OPTS = -DADDONS_TO_BUILD=imagedecoder.heif

$(eval $(cmake-package))
