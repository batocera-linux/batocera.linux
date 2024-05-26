################################################################################
#
# hatari
#
################################################################################

HATARI_VERSION = v2.5.0
HATARI_SOURCE = hatari-$(HATARI_VERSION).tar.gz
HATARI_SITE = https://github.com/hatari/hatari.git
HATARI_SITE_METHOD=git
HATARI_LICENSE = GPLv3
HATARI_DEPENDENCIES = sdl2 zlib libpng libcapsimage

HATARI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
HATARI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HATARI_CONF_OPTS += -DCAPSIMAGE_INCLUDE_DIR="($STAGING_DIR)/usr/include/caps"

define HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/hatari $(TARGET_DIR)/usr/bin/hatari
        mkdir -p $(TARGET_DIR)/usr/share/hatari
endef

define HATARI_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -D -m 0644 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/hatari/atarist.hatari.keys \
	        $(TARGET_DIR)/usr/share/evmapy/atarist.hatari.keys
endef

HATARI_POST_INSTALL_TARGET_HOOKS = HATARI_INSTALL_EVMAPY

$(eval $(cmake-package))
