################################################################################
#
# HATARI
#
################################################################################
# Version.: Release on Sep 17, 2020
HATARI_VERSION = v2.3.1
HATARI_SOURCE = hatari-$(HATARI_VERSION).tar.gz
HATARI_SITE = https://git.tuxfamily.org/hatari/hatari.git/snapshot
HATARI_LICENSE = GPLv3
HATARI_DEPENDENCIES = sdl2 zlib libpng capsimg

HATARI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
HATARI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/hatari $(TARGET_DIR)/usr/bin/hatari
        mkdir -p $(TARGET_DIR)/usr/share/hatari
endef

$(eval $(cmake-package))
