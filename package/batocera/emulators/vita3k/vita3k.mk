################################################################################
#
# vita3k
#
################################################################################
# Version: Commits on Aug 25, 2024
VITA3K_VERSION = f01a4e9b63583aa901f37a54523360be33034ccb
VITA3K_SITE = https://github.com/vita3k/vita3k
VITA3K_SITE_METHOD=git
VITA3K_GIT_SUBMODULES=YES
VITA3K_LICENSE = GPLv3
VITA3K_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf zlib libogg libvorbis python-ruamel-yaml
VITA3K_EXTRACT_DEPENDENCIES = host-libcurl

VITA3K_SUPPORTS_IN_SOURCE_BUILD = NO

VITA3K_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release \
                   -DBUILD_SHARED_LIBS=OFF \
                   -DUSE_DISCORD_RICH_PRESENCE=OFF \
                   -DUSE_VITA3K_UPDATE=OFF \
                   -DBUILD_EXTERNAL=ON

ifeq ($(BR2_x86_64),y)
VITA3K_FFMPEG_NAME=ffmpeg-linux-x64.zip
else ifeq ($(BR2_aarch64),y)
VITA3K_FFMPEG_NAME=ffmpeg-linux-arm64.zip
endif

VITA3K_FFMPEG_VER=$(shell cd "$(DL_DIR)/$(VITA3K_DL_SUBDIR)/git/external/ffmpeg" \
    && git rev-parse --short HEAD)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ZEN3),y)
    VITA3K_CONF_OPTS += -DXXH_X86DISPATCH_ALLOW_AVX=ON
else
    VITA3K_CONF_OPTS += -DXXH_X86DISPATCH_ALLOW_AVX=OFF
endif

define VITA3K_GET_SUBMODULE
    mkdir -p $(@D)/external
    cd $(@D)/external && git clone https://github.com/Vita3K/nativefiledialog-cmake
endef

define VITA3K_FFMPEG_ZIP
    mkdir -p $(@D)/buildroot-build/external
    $(HOST_DIR)/bin/curl -L \
        https://github.com/Vita3K/ffmpeg-core/releases/download/${VITA3K_FFMPEG_VER}/${VITA3K_FFMPEG_NAME} \
        -o $(@D)/buildroot-build/external/ffmpeg.zip
endef

define VITA3K_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vita3k/
	cp -R $(@D)/buildroot-build/bin/* $(TARGET_DIR)/usr/bin/vita3k/
endef

define VITA3K_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/vita3k/psvita.vita3k.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

VITA3K_POST_EXTRACT_HOOKS = VITA3K_GET_SUBMODULE
VITA3K_POST_EXTRACT_HOOKS += VITA3K_FFMPEG_ZIP
VITA3K_POST_INSTALL_TARGET_HOOKS = VITA3K_INSTALL_EVMAPY

$(eval $(cmake-package))
