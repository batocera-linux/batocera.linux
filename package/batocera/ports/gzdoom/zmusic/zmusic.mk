################################################################################
#
# zmusic
#
################################################################################

ZMUSIC_VERSION = 1.1.9
ZMUSIC_SITE = $(call github,coelckers,ZMusic,$(ZMUSIC_VERSION))
ZMUSIC_LICENSE = GPLv3
ZMUSIC_DEPENDENCIES = zlib mpg123 libsndfile alsa-lib
HOST_ZMUSIC_DEPENDENCIES = zlib mpg123 libsndfile alsa-lib

ZMUSIC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define ZMUSIC_INSTALL_TARGET_CMDS
    cp $(@D)/source/libzmusic* $(TARGET_DIR)/usr/lib/
endef

HOST_ZMUSIC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$(STAGING_DIR)/usr"

$(eval $(cmake-package))
$(eval $(host-cmake-package))
