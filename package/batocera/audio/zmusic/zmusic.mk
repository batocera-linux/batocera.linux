################################################################################
#
# zmusic
#
################################################################################
ZMUSIC_VERSION = 1.1.14
ZMUSIC_SITE = $(call github,coelckers,ZMusic,$(ZMUSIC_VERSION))
ZMUSIC_LICENSE = GPLv3
ZMUSIC_INSTALL_STAGING = YES
ZMUSIC_DEPENDENCIES = alsa-lib fluidsynth libglib2 libsndfile mpg123 zlib

ZMUSIC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define ZMUSIC_INSTALL_TARGET_CMDS
    cp -d $(@D)/source/libzmusic* $(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))
