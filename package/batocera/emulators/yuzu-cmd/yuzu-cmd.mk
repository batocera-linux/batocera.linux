################################################################################
#
# YUZU-CMD
#
################################################################################
# Version.: Commits on Oct 11, 2021
YUZU_CMD_VERSION = mainline-0-775
YUZU_CMD_SITE = https://github.com/yuzu-emu/yuzu-mainline.git
YUZU_CMD_SITE_METHOD=git
YUZU_CMD_GIT_SUBMODULES=YES
YUZU_CMD_LICENSE = GPLv2
YUZU_CMD_DEPENDENCIES = sdl2 fmt boost ffmpeg zstd catch2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
YUZU_CMD_SUPPORTS_IN_SOURCE_BUILD = NO

YUZU_CMD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
YUZU_CMD_CONF_OPTS += -DENABLE_SDL2=ON
YUZU_CMD_CONF_OPTS += -DARCHITECTURE_x86_64=ON
YUZU_CMD_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
YUZU_CMD_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
YUZU_CMD_CONF_OPTS += -DENABLE_QT=OFF

YUZU_CMD_CONF_ENV += LDFLAGS=-lpthread ARCHITECTURE_x86_64=1

define YUZU_CMD_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib/yuzu

        $(INSTALL) -D $(@D)/buildroot-build/bin/yuzu-cmd $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
