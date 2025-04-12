################################################################################
#
# citron
#
################################################################################
# Version: Commits on Apr 10, 2025
CITRON_VERSION = v0.6.1-canary-refresh
CITRON_SITE = https://git.citron-emu.org/Citron/Citron.git
CITRON_SITE_METHOD=git
CITRON_GIT_SUBMODULES=YES
CITRON_LICENSE = GPLv2
CITRON_DEPENDENCIES += boost catch2 enet ffmpeg fmt json-for-modern-cpp libzip lz4
CITRON_DEPENDENCIES += opus qt6base qt6tools qt6multimedia sdl2 stb zlib zstd

CITRON_SUPPORTS_IN_SOURCE_BUILD = NO

CITRON_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRON_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CITRON_CONF_OPTS += -DENABLE_SDL2=ON
CITRON_CONF_OPTS += -DCITRON_USE_EXTERNAL_SDL2=OFF
CITRON_CONF_OPTS += -DENABLE_QT=ON
CITRON_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON
CITRON_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
CITRON_CONF_OPTS += -DCITRON_TESTS=OFF
CITRON_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRON_CONF_OPTS += -DCITRON_DOWNLOAD_ANDROID_VVL=OFF
CITRON_CONF_OPTS += -DCITRON_ENABLE_PORTABLE=OFF
CITRON_CONF_OPTS += -DCMAKE_CXX_FLAGS=-Wno-error=shadow

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    CITRON_DEPENDENCIES += host-glslang vulkan-headers vulkan-loader
endif

define CITRON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib/citron
    $(INSTALL) -D $(@D)/buildroot-build/bin/citron $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/citron-cmd $(TARGET_DIR)/usr/bin/
    $(INSTALL) -D $(@D)/buildroot-build/bin/citron-room $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
