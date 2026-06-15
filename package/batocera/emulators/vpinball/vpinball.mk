################################################################################
#
# vpinball
#
################################################################################
# Version: Commits on Jun 10, 2026
VPINBALL_VERSION = 892deb5c5a0530cf0b4713feae401ae266899921
VPINBALL_SITE = $(call github,vpinball,vpinball,$(VPINBALL_VERSION))
VPINBALL_LICENSE = GPLv3+
VPINBALL_LICENSE_FILES = LICENSE
VPINBALL_DEPENDENCIES = host-libcurl host-cmake libfreeimage libpinmame
VPINBALL_DEPENDENCIES += libdmdutil libdof sdl3 sdl3_image sdl3_ttf
VPINBALL_DEPENDENCIES += bgfx ffmpeg libaltsound libwinevbs
VPINBALL_SUPPORTS_IN_SOURCE_BUILD = NO
VPINBALL_EMULATOR_INFO = vpinball.emulator.yml

VPINBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VPINBALL_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
VPINBALL_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

# Handle supported target platforms cleanly using standard Buildroot variables
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_MAINLINE),y)
    VPX_SOURCE = CMakeLists_bgfx-linux-aarch64.txt
    VPX_SOURCE_DIR = linux-aarch64
    VPINBALL_CONF_OPTS += -DBUILD_RK3588=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    VPX_SOURCE = CMakeLists_bgfx-linux-aarch64.txt
    VPX_SOURCE_DIR = linux-aarch64
    VPINBALL_CONF_OPTS += -DBUILD_RPI=ON
else ifeq ($(BR2_aarch64),y)
    VPX_SOURCE = CMakeLists_bgfx-linux-aarch64.txt
    VPX_SOURCE_DIR = linux-aarch64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    VPX_SOURCE = CMakeLists_bgfx-linux-x64.txt
    VPX_SOURCE_DIR = linux-x64
endif

define VPINBALL_CMAKE_HACKS
    # Copy the correct platform CMakeLists to the root directory
    cp $(@D)/make/$(VPX_SOURCE) $(@D)/CMakeLists.txt

    # Delete only the bundled libraries we want to override with Buildroot packages
    rm -rf $(@D)/third-party/include/bgfx
    rm -rf $(@D)/third-party/include/bx
    rm -rf $(@D)/third-party/include/bimg
    rm -rf $(@D)/third-party/include/SDL3
    rm -rf $(@D)/third-party/include/FreeImage

    # Redirect libwinevbs header paths to staging
    $(SED) 's:\$${CMAKE_SOURCE_DIR}/third-party/include/libwinevbs/atl/include:$(STAGING_DIR)/usr/include/libwinevbs/atl:g' \
        $(@D)/CMakeLists.txt
    $(SED) 's:\$${CMAKE_SOURCE_DIR}/third-party/include/libwinevbs/atlmfc/include:$(STAGING_DIR)/usr/include/libwinevbs/atlmfc:g' \
        $(@D)/CMakeLists.txt
    $(SED) 's:\$${CMAKE_SOURCE_DIR}/third-party/include/libwinevbs/wine/include:$(STAGING_DIR)/usr/include/libwinevbs/wine:g' \
        $(@D)/CMakeLists.txt

    # Redirect target link paths to staging
    $(SED) 's:\$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$(VPX_SOURCE_DIR):$(STAGING_DIR)/usr/lib:g' \
        $(@D)/CMakeLists.txt

    # Redirect plugin library paths to staging
    for f in $(@D)/make/CMakeLists_plugin_*.txt; do \
        $(SED) 's:\$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/\$${PluginPlatform}-\$${PluginArch}:$(STAGING_DIR)/usr/lib:g' $$f; \
    done
endef

VPINBALL_PRE_CONFIGURE_HOOKS += VPINBALL_CMAKE_HACKS

define VPINBALL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vpinball
    # Install binary
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/VPinballX_BGFX \
        $(TARGET_DIR)/usr/bin/vpinball/VPinballX_BGFX
    # Copy assets and plugins folders
    cp -R $(@D)/buildroot-build/plugins $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/assets $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/scripts $(TARGET_DIR)/usr/bin/vpinball/
    # Install custom scraper script
    $(INSTALL) -D -m 0755 $(VPINBALL_PKGDIR)/batocera-vpx-scraper.py \
        $(TARGET_DIR)/usr/bin/batocera-vpx-scraper
endef

define VPINBALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(VPINBALL_PKGDIR)/vpinball.keys $(TARGET_DIR)/usr/share/evmapy
endef

VPINBALL_POST_INSTALL_TARGET_HOOKS += VPINBALL_EVMAPY

$(eval $(cmake-package))
$(eval $(emulator-info-package))
