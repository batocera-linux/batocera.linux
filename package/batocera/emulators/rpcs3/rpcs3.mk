################################################################################
#
# rpcs3
#
################################################################################
# Version: 0.0.29-15608 - Commits on Sep 7, 2023
RPCS3_VERSION = 009d8e13dac86ed8f73d58ffd0e9b073c788f628
RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES += alsa-lib batocera-llvm faudio ffmpeg libevdev libxml2
RPCS3_DEPENDENCIES += libglew libglu libpng libusb mesa3d ncurses openal
RPCS3_DEPENDENCIES += qt6base qt6declarative qt6multimedia qt6svg wolfssl 

RPCS3_SUPPORTS_IN_SOURCE_BUILD = NO

RPCS3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPCS3_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=ON
RPCS3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RPCS3_CONF_OPTS += -DUSE_NATIVE_INSTRUCTIONS=OFF
RPCS3_CONF_OPTS += -DLLVM_DIR=$(STAGING_DIR)/usr/lib/cmake/llvm/
RPCS3_CONF_OPTS += -DUSE_PRECOMPILED_HEADERS=OFF
RPCS3_CONF_OPTS += -DSTATIC_LINK_LLVM=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_CURL=ON
RPCS3_CONF_OPTS += -DUSE_LIBEVDEV=ON
# sdl controller config seems broken...
RPCS3_CONF_OPTS += -DUSE_SDL=OFF
# this is ugly, but necessary... for now...
RPCS3_CONF_OPTS += -DFFMPEG_LIB_AVCODEC=../3rdparty/ffmpeg/lib/linux/ubuntu-22.04/x86_64/libavcodec.a
RPCS3_CONF_OPTS += -DFFMPEG_LIB_AVFORMAT=../3rdparty/ffmpeg/lib/linux/ubuntu-22.04/x86_64/libavformat.a
RPCS3_CONF_OPTS += -DFFMPEG_LIB_AVUTIL=../3rdparty/ffmpeg/lib/linux/ubuntu-22.04/x86_64/libavutil.a
RPCS3_CONF_OPTS += -DFFMPEG_LIB_SWSCALE=../3rdparty/ffmpeg/lib/linux/ubuntu-22.04/x86_64/libswscale.a
RPCS3_CONF_OPTS += -DFFMPEG_LIB_SWRESAMPLE=../3rdparty/ffmpeg/lib/linux/ubuntu-22.04/x86_64/libswresample.a

RPCS3_CONF_ENV = LIBS="-ncurses -ltinfo"

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    RPCS3_CONF_OPTS += -DUSE_VULKAN=ON
else
    RPCS3_CONF_OPTS += -DUSE_VULKAN=OFF
endif

define RPCS3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
		$(MAKE) -C $(@D)/buildroot-build
endef

define RPCS3_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -D -m 0644 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/rpcs3/evmapy.keys \
	    $(TARGET_DIR)/usr/share/evmapy/ps3.keys
endef

RPCS3_POST_INSTALL_TARGET_HOOKS = RPCS3_INSTALL_EVMAPY

$(eval $(cmake-package))
