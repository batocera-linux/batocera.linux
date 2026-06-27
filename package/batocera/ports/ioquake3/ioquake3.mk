################################################################################
#
# ioquake3
#
################################################################################
# Version: Commits on Mar 9, 2026
IOQUAKE3_VERSION = 5956299e80b29ef3891bcec8e99cd3e680f34b1a
IOQUAKE3_SITE = $(call github,ioquake,ioq3,$(IOQUAKE3_VERSION))
IOQUAKE3_LICENSE = GPL-2.0
IOQUAKE3_LICENSE_FILE = COPYING.txt
IOQUAKE3_EMULATOR_INFO = ioquake3.emulator.yml

IOQUAKE3_DEPENDENCIES = freetype libcurl libogg libvorbis libzlib openal opus sdl2

IOQUAKE3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
IOQUAKE3_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr/bin/ioquake3
IOQUAKE3_CONF_OPTS += -DBUILD_SERVER=OFF
IOQUAKE3_CONF_OPTS += -DBUILD_GAME_LIBRARIES=OFF
IOQUAKE3_CONF_OPTS += -DBUILD_GAME_QVMS=OFF
IOQUAKE3_CONF_OPTS += -DUSE_FREETYPE=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
    IOQUAKE3_DEPENDENCIES += libgles
else ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    IOQUAKE3_DEPENDENCIES += libgl
endif

define IOQUAKE3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ioquake3/quake3.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

IOQUAKE3_POST_INSTALL_TARGET_HOOKS += IOQUAKE3_EVMAPY

$(eval $(cmake-package))
$(eval $(emulator-info-package))
