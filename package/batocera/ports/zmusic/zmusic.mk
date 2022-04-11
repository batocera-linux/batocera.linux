################################################################################
#
# ZMUSIC
#
################################################################################

ZMUSIC_VERSION = 1.1.8
ZMUSIC_SITE = $(call github,coelckers,ZMusic,$(ZMUSIC_VERSION))
ZMUSIC_LICENSE = GPL v3
ZMUSIC_DEPENDENCIES = zlib mpg123 libsndfile alsa-lib

ZMUSIC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
