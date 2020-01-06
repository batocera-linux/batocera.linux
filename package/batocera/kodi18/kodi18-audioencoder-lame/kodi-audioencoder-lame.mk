################################################################################
#
# kodi-audioencoder-lame
#
################################################################################

KODI18_AUDIOENCODER_LAME_VERSION = 2.0.3-Leia
KODI18_AUDIOENCODER_LAME_SITE = $(call github,xbmc,audioencoder.lame,$(KODI18_AUDIOENCODER_LAME_VERSION))
KODI18_AUDIOENCODER_LAME_LICENSE = GPL-2.0+
KODI18_AUDIOENCODER_LAME_LICENSE_FILES = src/EncoderLame.cpp
KODI18_AUDIOENCODER_LAME_DEPENDENCIES = kodi18 lame
KODI18_AUDIOENCODER_LAME_CONF_OPTS += \
	-DLAME_INCLUDE_DIRS=$(STAGING_DIR)/usr/include

$(eval $(cmake-package))
