################################################################################
#
# vpinball
#
################################################################################
# Version: Commits on Oct 14, 2026
VPINBALL_VERSION = 68afa2a9056131c7065959d7b0915b9cc38d09dc
VPINBALL_REVISION = 6231
VPINBALL_SITE = $(call github,vpinball,vpinball,$(VPINBALL_VERSION))
VPINBALL_LICENSE = GPLv3+
VPINBALL_LICENSE_FILES = LICENSE
VPINBALL_DEPENDENCIES = host-libcurl host-cmake libfreeimage-vpinball libpinmame
VPINBALL_DEPENDENCIES += libdmdutil libdof sdl3 sdl3_image sdl3_ttf
VPINBALL_DEPENDENCIES += bgfx ffmpeg libaltsound libwinevbs openxr-sdk vulkan-headers
VPINBALL_DEPENDENCIES += libspatialaudio zlib
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
VPINBALL_CONF_OPTS += -DFREEIMAGE_INCLUDE_DIR=$(STAGING_DIR)/libfreeimage-vpinball/include
VPINBALL_CONF_OPTS += -DFREEIMAGE_LIBRARY=$(STAGING_DIR)/libfreeimage-vpinball/lib/libfreeimage.a

define VPINBALL_SET_GIT_VERSION
	$(SED) 's/9999/$(VPINBALL_REVISION)/;s/unknown/$(shell echo $(VPINBALL_VERSION) | cut -c1-9)/' \
		$(@D)/src/core/git_version.h
endef

VPINBALL_POST_EXTRACT_HOOKS += VPINBALL_SET_GIT_VERSION

VPINBALL_MEMMAPS_VERSION = 68c1b3373ba74cd07f42fba9d56db63ea28212dc
VPINBALL_GAMEDEFS_VERSION = 6eece7e53de9463bf783b9476ce3aeb98e2e7256
VPINBALL_EXTRA_DOWNLOADS = \
    https://github.com/tomlogic/pinball-memory-maps/archive/$(VPINBALL_MEMMAPS_VERSION).tar.gz \
    https://github.com/vpinball/pinmame-game-defs/archive/$(VPINBALL_GAMEDEFS_VERSION).tar.gz

define VPINBALL_EXTRACT_PINMAME_DATA
	mkdir -p $(@D)/pinmame-data $(@D)/third-party/memmaps $(@D)/third-party/gamedefs
	$(TAR) -xf $(VPINBALL_DL_DIR)/$(VPINBALL_MEMMAPS_VERSION).tar.gz -C $(@D)/pinmame-data
	$(TAR) -xf $(VPINBALL_DL_DIR)/$(VPINBALL_GAMEDEFS_VERSION).tar.gz -C $(@D)/pinmame-data
	cd $(@D)/pinmame-data/pinball-memory-maps-$(VPINBALL_MEMMAPS_VERSION) && \
		cp -r index.json maps platforms $(@D)/third-party/memmaps/
	cd $(@D)/pinmame-data/pinmame-game-defs-$(VPINBALL_GAMEDEFS_VERSION) && \
		cp -r catalog machines controllers $(@D)/third-party/gamedefs/
endef

VPINBALL_POST_EXTRACT_HOOKS += VPINBALL_EXTRACT_PINMAME_DATA

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
