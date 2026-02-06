################################################################################
#
# vpinball
#
################################################################################
# Version: Commits on Feb 3, 2026
VPINBALL_VERSION = bb815858da96cbe780f516f41a258b5daf90b386
VPINBALL_SITE = $(call github,vpinball,vpinball,$(VPINBALL_VERSION))
VPINBALL_LICENSE = GPLv3+
VPINBALL_LICENSE_FILES = LICENSE
VPINBALL_DEPENDENCIES = host-libcurl host-cmake libfreeimage libpinmame libaltsound libdmdutil libdof sdl3 sdl3_image sdl3_ttf ffmpeg
VPINBALL_SUPPORTS_IN_SOURCE_BUILD = NO
VPINBALL_EMULATOR_INFO = vpinball.emulator.yml

# handle supported target platforms
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO),y)
    SOURCE = CMakeLists_bgfx-linux-aarch64.txt
    SOURCE_DIR = linux-aarch64
    ARCH = aarch64
    VPINBALL_CONF_OPTS += "-DBUILD_RK3588=ON"
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    SOURCE = CMakeLists_bgfx-linux-aarch64.txt
    SOURCE_DIR = linux-aarch64
    ARCH = aarch64
    VPINBALL_CONF_OPTS += "-DBUILD_RPI=ON"
else ifeq ($(BR2_aarch64),y)
    SOURCE = CMakeLists_bgfx-linux-aarch64.txt
    SOURCE_DIR = linux-aarch64
    ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    SOURCE = CMakeLists_bgfx-linux-x64.txt
    SOURCE_DIR = linux-x64
    ARCH = x86_64
endif

define VPINBALL_BUILD_BGFX
    $(eval BGFX_CMAKE_VERSION = $(shell grep 'BGFX_CMAKE_VERSION=' $(@D)/platforms/config.sh | cut -d= -f2))
    $(eval BGFX_PATCH_SHA = $(shell grep 'BGFX_PATCH_SHA=' $(@D)/platforms/config.sh | cut -d= -f2))
    mkdir -p $(@D)/external-build/bgfx
    $(HOST_DIR)/bin/curl -sL https://github.com/bkaradzic/bgfx.cmake/releases/download/v$(BGFX_CMAKE_VERSION)/bgfx.cmake.v$(BGFX_CMAKE_VERSION).tar.gz \
        -o $(@D)/external-build/bgfx/bgfx.cmake.tar.gz
    $(TAR) -xzf $(@D)/external-build/bgfx/bgfx.cmake.tar.gz -C $(@D)/external-build/bgfx
    $(HOST_DIR)/bin/curl -sL https://github.com/vbousquet/bgfx/archive/$(BGFX_PATCH_SHA).tar.gz \
        -o $(@D)/external-build/bgfx/bgfx-patch.tar.gz
    $(TAR) -xzf $(@D)/external-build/bgfx/bgfx-patch.tar.gz -C $(@D)/external-build/bgfx
    rm -rf $(@D)/external-build/bgfx/bgfx.cmake/bgfx
    mv $(@D)/external-build/bgfx/bgfx-$(BGFX_PATCH_SHA) $(@D)/external-build/bgfx/bgfx.cmake/bgfx
    cd $(@D)/external-build/bgfx/bgfx.cmake && \
    $(BR2_CMAKE) -S. \
        -DCMAKE_C_COMPILER="$(TARGET_CC)" \
        -DCMAKE_CXX_COMPILER="$(TARGET_CXX)" \
        -DCMAKE_SYSROOT="$(STAGING_DIR)" \
        -DCMAKE_FIND_ROOT_PATH="$(STAGING_DIR)" \
        -DCMAKE_SYSTEM_NAME=Linux \
        -DCMAKE_SYSTEM_PROCESSOR=$(ARCH) \
        -DBGFX_LIBRARY_TYPE=SHARED \
        -DBGFX_BUILD_TOOLS=OFF \
        -DBGFX_BUILD_EXAMPLES=OFF \
        -DBGFX_CONFIG_MULTITHREADED=ON \
        -DBGFX_CONFIG_MAX_FRAME_BUFFERS=256 \
        -DBGFX_WITH_WAYLAND=OFF \
        -DCMAKE_BUILD_TYPE=Release \
        -B build
    $(BR2_CMAKE) --build $(@D)/external-build/bgfx/bgfx.cmake/build -- -j$(PARALLEL_JOBS)
    mkdir -p $(@D)/third-party/include $(@D)/third-party/runtime-libs/$(SOURCE_DIR)
    cp -r $(@D)/external-build/bgfx/bgfx.cmake/bgfx/include/bgfx $(@D)/third-party/include/
    cp -r $(@D)/external-build/bgfx/bgfx.cmake/bimg/include/bimg $(@D)/third-party/include/
    cp -r $(@D)/external-build/bgfx/bgfx.cmake/bx/include/bx $(@D)/third-party/include/
    cp $(@D)/external-build/bgfx/bgfx.cmake/build/cmake/bgfx/libbgfx.so $(@D)/third-party/runtime-libs/$(SOURCE_DIR)/
endef

VPINBALL_PRE_CONFIGURE_HOOKS += VPINBALL_BUILD_BGFX

define VPINBALL_CMAKE_HACKS
    # copy platform CMakeLists
    cp $(@D)/make/$(SOURCE) $(@D)/CMakeLists.txt
    # add staging paths for system libs (keep third-party for local bgfx)
    $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/include:$(STAGING_DIR)/usr/include\n   $${CMAKE_SOURCE_DIR}/third-party/include:g' $(@D)/CMakeLists.txt
    $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$(SOURCE_DIR):$(STAGING_DIR)/usr/lib\n   $${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$(SOURCE_DIR):g' $(@D)/CMakeLists.txt
    # update plugin CMakeLists - add staging paths
    for f in $(@D)/make/CMakeLists_plugin_*.txt; do \
        $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/include:$(STAGING_DIR)/usr/include\n      $${CMAKE_SOURCE_DIR}/third-party/include:g' $$f; \
        $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$${PluginPlatform}-$${PluginArch}:$(STAGING_DIR)/usr/lib\n      $${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$${PluginPlatform}-$${PluginArch}:g' $$f; \
    done
    # make tmp
    rm -rf $(@D)/tmp
    mkdir $(@D)/tmp
endef

VPINBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VPINBALL_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
VPINBALL_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

define VPINBALL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vpinball
    # install binary
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/VPinballX_BGFX \
        $(TARGET_DIR)/usr/bin/vpinball/VPinballX_BGFX
    # copy folders
    cp -R $(@D)/buildroot-build/plugins $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/assets $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/scripts $(TARGET_DIR)/usr/bin/vpinball/
    # install bgfx runtime library (bundled with vpinball, not system-wide on target)
    $(INSTALL) -D -m 0755 $(@D)/third-party/runtime-libs/$(SOURCE_DIR)/libbgfx.so \
        $(TARGET_DIR)/usr/bin/vpinball/libbgfx.so
    $(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/vpinball/batocera-vpx-scraper.py \
        $(TARGET_DIR)/usr/bin/batocera-vpx-scraper
endef

define VPINBALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/vpinball/vpinball.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

VPINBALL_PRE_CONFIGURE_HOOKS += VPINBALL_CMAKE_HACKS

VPINBALL_POST_INSTALL_TARGET_HOOKS += VPINBALL_EVMAPY

$(eval $(cmake-package))
$(eval $(emulator-info-package))