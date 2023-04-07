################################################################################
#
# kodi20-audioencoder-lame
#
################################################################################

KODI20_AUDIOENCODER_LAME_VERSION = 20.3.0-Nexus
KODI20_AUDIOENCODER_LAME_SITE = $(call github,xbmc,audioencoder.lame,$(KODI20_AUDIOENCODER_LAME_VERSION))
KODI20_AUDIOENCODER_LAME_LICENSE = GPL-2.0+
KODI20_AUDIOENCODER_LAME_LICENSE_FILES = LICENSE.md
KODI20_AUDIOENCODER_LAME_DEPENDENCIES = kodi20 lame
KODI20_AUDIOENCODER_LAME_CONF_OPTS += \
	-DLAME_INCLUDE_DIRS=$(STAGING_DIR)/usr/include

ifeq ($(BR2_ENABLE_LOCALE),)
KODI20_AUDIOENCODER_LAME_DEPENDENCIES += libiconv
endif

$(eval $(cmake-package))
