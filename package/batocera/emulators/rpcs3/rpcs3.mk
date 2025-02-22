################################################################################
#
# rpcs3
#
################################################################################
# Version: 0.0.34-17506, Commits on Feb 22, 2025
RPCS3_VERSION = 796a2371281b760c4611e6c0ad9ebd75b8837420
RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES += alsa-lib llvm faudio ffmpeg libevdev libxml2 libglew
RPCS3_DEPENDENCIES += libglu libpng libusb mesa3d ncurses openal opencv4 rtmpdump
RPCS3_DEPENDENCIES += qt6base qt6declarative qt6multimedia qt6svg wolfssl libcurl

RPCS3_SUPPORTS_IN_SOURCE_BUILD = NO

RPCS3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPCS3_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=ON
RPCS3_CONF_OPTS += -DCMAKE_CXX_FLAGS="-fno-function-sections"
RPCS3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RPCS3_CONF_OPTS += -DUSE_NATIVE_INSTRUCTIONS=OFF
RPCS3_CONF_OPTS += -DLLVM_DIR=$(STAGING_DIR)/usr/lib/cmake/llvm/
RPCS3_CONF_OPTS += -DUSE_PRECOMPILED_HEADERS=OFF
RPCS3_CONF_OPTS += -DSTATIC_LINK_LLVM=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_CURL=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBUSB=ON
RPCS3_CONF_OPTS += -DUSE_LIBEVDEV=ON

ifeq ($(BR2_PACKAGE_SDL2),y)
    RPCS3_CONF_OPTS += -DUSE_SDL=ON
else
    RPCS3_CONF_OPTS += -DUSE_SDL=OFF
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    RPCS3_CONF_OPTS += -DUSE_VULKAN=ON
else
    RPCS3_CONF_OPTS += -DUSE_VULKAN=OFF
endif

$(eval $(cmake-package))
