################################################################################
#
# suyu
#
################################################################################
# Version: Commits on Jul 4, 2024
SUYU_VERSION = 4eb41467f8cf39d666372b5ea78694df970252a3
SUYU_SITE = https://git.suyu.dev/suyu/suyu.git
SUYU_SITE_METHOD=git
SUYU_GIT_SUBMODULES=YES
SUYU_LICENSE = GPLv2
SUYU_DEPENDENCIES = qt6base qt6tools qt6multimedia fmt boost ffmpeg \
                    zstd zlib libzip lz4 catch2 sdl2 opus json-for-modern-cpp

SUYU_SUPPORTS_IN_SOURCE_BUILD = NO

SUYU_CONF_ENV += LDFLAGS=-lpthread ARCHITECTURE_x86_64=1

SUYU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SUYU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SUYU_CONF_OPTS += -DARCHITECTURE_x86_64=ON
SUYU_CONF_OPTS += -DENABLE_SDL2=ON
SUYU_CONF_OPTS += -DENABLE_QT6=ON
SUYU_CONF_OPTS += -DSUYU_USE_EXTERNAL_SDL2=OFF
SUYU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
SUYU_CONF_OPTS += -DSUYU_TESTS=OFF
SUYU_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    SUYU_DEPENDENCIES += host-glslang vulkan-headers vulkan-loader
endif

define SUYU_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib/suyu
    $(INSTALL) -D $(@D)/buildroot-build/bin/suyu $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/suyu-cmd $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/suyu-room $(TARGET_DIR)/usr/bin/
    #evmap config
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/suyu/switch.suyu.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
