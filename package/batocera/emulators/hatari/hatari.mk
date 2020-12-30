################################################################################
#
# HATARI
#
################################################################################
# Version.: Release on Sep 17, 2020
HATARI_VERSION = v2.3.1
HATARI_SOURCE = hatari-$(HATARI_VERSION).tar.gz
HATARI_SITE = https://git.tuxfamily.org/hatari/hatari.git/snapshot/

HATARI_LICENSE = GPLv3
HATARI_DEPENDENCIES = sdl2

define HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/hatari $(TARGET_DIR)/usr/bin/hatari
        mkdir -p $(TARGET_DIR)/usr/share/hatari
endef

$(eval $(cmake-package))
