################################################################################
#
# pcsx2
#
################################################################################
#Version: Commits on Oct 12, 2023
PCSX2_VERSION = v1.7.5105
PCSX2_SITE = https://github.com/pcsx2/pcsx2.git
PCSX2_SITE_METHOD = git
PCSX2_GIT_SUBMODULES = YES
PCSX2_LICENSE = GPLv3
PCSX2_LICENSE_FILE = COPYING.GPLv3

PCSX2_SUPPORTS_IN_SOURCE_BUILD = NO

PCSX2_DEPENDENCIES += xorgproto alsa-lib freetype zlib libpng
PCSX2_DEPENDENCIES += libaio portaudio libsoundtouch sdl2 libpcap yaml-cpp
PCSX2_DEPENDENCIES += libsamplerate fmt wxwidgets libgtk3 qt6base qt6tools qt6svg

PCSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PCSX2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PCSX2_CONF_OPTS += -DPCSX2_TARGET_ARCHITECTURES=x86_64
PCSX2_CONF_OPTS += -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=TRUE
PCSX2_CONF_OPTS += -DQT_BUILD=TRUE
PCSX2_CONF_OPTS += -DENABLE_TESTS=OFF
PCSX2_CONF_OPTS += -DUSE_SYSTEM_LIBS=AUTO
PCSX2_CONF_OPTS += -DUSE_VTUNE=OFF
PCSX2_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
PCSX2_CONF_OPTS += -DLTO_PCSX2_CORE=ON
PCSX2_CONF_OPTS += -DUSE_ACHIEVEMENTS=ON
# The following flag is misleading and *needed* ON to avoid doing -march=native
PCSX2_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON

ifeq ($(BR2_PACKAGE_XORG7),y)
    PCSX2_CONF_OPTS += -DX11_API=ON
else
    PCSX2_CONF_OPTS += -DX11_API=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
    PCSX2_CONF_OPTS += -DWAYLAND_API=ON
else
    PCSX2_CONF_OPTS += -DWAYLAND_API=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    PCSX2_CONF_OPTS += -DUSE_OPENGL=ON
else
    PCSX2_CONF_OPTS += -DUSE_OPENGL=OFF
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    PCSX2_CONF_OPTS += -DUSE_VULKAN=ON
else
    PCSX2_CONF_OPTS += -DUSE_VULKAN=OFF
endif

define PCSX2_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/buildroot-build/bin/pcsx2-qt \
        $(TARGET_DIR)/usr/pcsx2/bin/pcsx2-qt
	cp -pr  $(@D)/bin/resources $(TARGET_DIR)/usr/pcsx2/bin/
    # use our SDL config
    rm $(TARGET_DIR)/usr/pcsx2/bin/resources/game_controller_db.txt
endef

define PCSX2_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/pcsx2/ps2.pcsx2.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_EVMAPY

define PCSX2_TEXTURES
	mkdir -p $(TARGET_DIR)/usr/pcsx2/bin/resources/textures
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/pcsx2/textures/ \
        $(TARGET_DIR)/usr/pcsx2/bin/resources/
endef

# Download and copy PCSX2 patches.zip to BIOS folder
define PCSX2_PATCHES
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/pcsx2
        $(HOST_DIR)/bin/curl -L https://github.com/PCSX2/pcsx2_patches/releases/download/latest/patches.zip -o $(TARGET_DIR)/usr/share/batocera/datainit/bios/pcsx2/patches.zip
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_TEXTURES
PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_PATCHES

$(eval $(cmake-package))
