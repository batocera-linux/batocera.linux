################################################################################
#
# YUZU
#
################################################################################
# Version.: Commits on Jul 16, 2020
YUZU_VERSION = 67db767dc1caa7ef4e6e4a3c9014d6cbb1e73274
YUZU_SITE = https://github.com/yuzu-emu/yuzu-mainline.git
YUZU_SITE_METHOD=git
YUZU_GIT_SUBMODULES=YES
YUZU_LICENSE = GPLv2
YUZU_DEPENDENCIES = qt5base qt5tools qt5multimedia fmt boost ffmpeg zstd catch2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
YUZU_SUPPORTS_IN_SOURCE_BUILD = NO

YUZU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
YUZU_CONF_OPTS += -DENABLE_SDL2=OFF
YUZU_CONF_OPTS += -DARCHITECTURE_x86_64=ON
YUZU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

YUZU_CONF_ENV += LDFLAGS=-lpthread ARCHITECTURE_x86_64=1

define YUZU_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib/yuzu

	$(INSTALL) -D $(@D)/buildroot-build/bin/yuzu $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
