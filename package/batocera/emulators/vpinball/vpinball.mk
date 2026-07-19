################################################################################
#
# vpinball
#
################################################################################
# Version: Commits on Jul 19, 2026
VPINBALL_VERSION = 9810f0e777d5d58cd798c5b765f92b709f8b9150
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
    VPINBALL_ARCH = aarch64
    VPINBALL_CONF_OPTS += -DBUILD_RK3588=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    VPINBALL_ARCH = aarch64
    VPINBALL_CONF_OPTS += -DBUILD_RPI=ON
else ifeq ($(BR2_aarch64),y)
    VPINBALL_ARCH = aarch64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    VPINBALL_ARCH = x64
endif

# Build against Buildroot's staging tree instead of the bundled third-party/ copies.
# USE_SYSTEM_LIBS makes the single root CMakeLists.txt search staging first, falling back
# to the bundled tree for what staging doesn't provide (serum/vni/pupdmd, vendored headers).
VPINBALL_CONF_OPTS += -DPLATFORM=linux
VPINBALL_CONF_OPTS += -DARCH=$(VPINBALL_ARCH)
VPINBALL_CONF_OPTS += -DRENDERER=BGFX
VPINBALL_CONF_OPTS += -DUSE_SYSTEM_LIBS=ON
VPINBALL_CONF_OPTS += -DSYSTEM_LIBS_INCLUDE_DIR=$(STAGING_DIR)/usr/include
VPINBALL_CONF_OPTS += -DSYSTEM_LIBS_LIB_DIR=$(STAGING_DIR)/usr/lib

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
