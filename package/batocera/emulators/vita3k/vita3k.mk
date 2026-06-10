################################################################################
#
# vita3k
#
################################################################################
# Version: Commits on Jun 10, 2026
VITA3K_VERSION = 7c567c18043bc83282b1d834dc027dae13e5a296
VITA3K_SITE = https://github.com/vita3k/vita3k
VITA3K_SITE_METHOD = git
VITA3K_GIT_SUBMODULES = YES
VITA3K_LICENSE = GPLv3
VITA3K_EMULATOR_INFO = vita3k.emulator.yml

VITA3K_SUPPORTS_IN_SOURCE_BUILD = NO

VITA3K_DEPENDENCIES += host-clang host-ninja python-ruamel-yaml libcurl
VITA3K_DEPENDENCIES += sdl3 sdl3_image sdl3_ttf zlib libogg libvorbis
VITA3K_DEPENDENCIES += boost pipewire qt6base qt6svg qt6tools qt6multimedia
VITA3K_EXTRACT_DEPENDENCIES = host-libcurl

ifeq ($(BR2_PACKAGE_WAYLAND),y)
VITA3K_DEPENDENCIES += wayland
endif

VITA3K_CMAKE_BACKEND = ninja

VITA3K_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang \
                    -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++ \
                    -DCMAKE_EXE_LINKER_FLAGS="-no-pie -lm -lstdc++" \
                    -DCMAKE_BUILD_TYPE=Release \
                    -DBUILD_SHARED_LIBS=OFF \
                    -DUSE_DISCORD_RICH_PRESENCE=OFF \
                    -DVITA3K_FORCE_SYSTEM_BOOST=ON \
                    -DSDL_HIDAPI=OFF

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
VITA3K_CONF_OPTS += -DXXH_X86DISPATCH_ALLOW_AVX=ON
else
VITA3K_CONF_OPTS += -DXXH_X86DISPATCH_ALLOW_AVX=OFF
endif

ifeq ($(BR2_x86_64),y)
VITA3K_FFMPEG_NAME=ffmpeg-linux-x64.zip
else ifeq ($(BR2_aarch64),y)
VITA3K_FFMPEG_NAME=ffmpeg-linux-arm64.zip
endif

VITA3K_FFMPEG_VER=$(shell cd "$(DL_DIR)/$(VITA3K_DL_SUBDIR)/git/external/ffmpeg" \
    && git rev-parse --short HEAD)

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

VITA3K_POST_EXTRACT_HOOKS += VITA3K_FFMPEG_ZIP

$(eval $(cmake-package))
$(eval $(emulator-info-package))
