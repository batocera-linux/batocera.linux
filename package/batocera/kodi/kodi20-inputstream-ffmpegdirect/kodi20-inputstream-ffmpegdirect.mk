################################################################################
#
# kodi20-inputstream-ffmpegdirect
#
################################################################################

KODI20_INPUTSTREAM_FFMPEGDIRECT_VERSION = 20.5.0-Nexus
KODI20_INPUTSTREAM_FFMPEGDIRECT_SITE = $(call github,xbmc,inputstream.ffmpegdirect,$(KODI20_INPUTSTREAM_FFMPEGDIRECT_VERSION))
KODI20_INPUTSTREAM_FFMPEGDIRECT_LICENSE = GPL-2.0+
KODI20_INPUTSTREAM_FFMPEGDIRECT_LICENSE_FILES = LICENSE.md
KODI20_INPUTSTREAM_FFMPEGDIRECT_DEPENDENCIES = bzip2 ffmpeg kodi20
KODI20_INPUTSTREAM_FFMPEGDIRECT_CONF_OPTS = \
	-DFFMPEG_PATH=$(STAGING_DIR)/usr

$(eval $(cmake-package))
