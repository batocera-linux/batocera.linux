################################################################################
#
# pcsx2
#
################################################################################

PCSX2_VERSION = v2.1.100
PCSX2_SITE = https://github.com/pcsx2/pcsx2.git
PCSX2_SITE_METHOD = git
PCSX2_GIT_SUBMODULES = YES
PCSX2_LICENSE = GPLv3
PCSX2_LICENSE_FILE = COPYING.GPLv3

PCSX2_SUPPORTS_IN_SOURCE_BUILD = NO

PCSX2_DEPENDENCIES += xorgproto alsa-lib freetype zlib libpng stenzek-shaderc
PCSX2_DEPENDENCIES += libaio portaudio libsoundtouch sdl2 libpcap yaml-cpp
PCSX2_DEPENDENCIES += libsamplerate fmt wxwidgets libgtk3 qt6base qt6tools qt6svg

PCSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PCSX2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PCSX2_CONF_OPTS += -DENABLE_TESTS=OFF
PCSX2_CONF_OPTS += -DUSE_SYSTEM_LIBS=AUTO
# The following flag is misleading and *needed* ON to avoid doing -march=native
PCSX2_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON
PCSX2_CONF_OPTS += -DSHADERC_INCLUDE_DIR=$(STAGING_DIR)/stenzek-shaderc/include
PCSX2_CONF_OPTS += -DSHADERC_LIBRARY=$(STAGING_DIR)/stenzek-shaderc/lib/libshaderc_shared.so

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

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    PCSX2_CONF_OPTS += -DUSE_VULKAN=ON
else
    PCSX2_CONF_OPTS += -DUSE_VULKAN=OFF
endif

define PCSX2_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/buildroot-build/bin/pcsx2-qt \
        $(TARGET_DIR)/usr/pcsx2/bin/pcsx2-qt
	cp -pr  $(@D)/bin/resources $(TARGET_DIR)/usr/pcsx2/bin/
    cp -pr  $(@D)/buildroot-build/bin/translations $(TARGET_DIR)/usr/pcsx2/bin/
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
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/ps2
    $(HOST_DIR)/bin/curl -L \
        https://github.com/PCSX2/pcsx2_patches/releases/download/latest/patches.zip -o \
        $(TARGET_DIR)/usr/share/batocera/datainit/bios/ps2/patches.zip
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_TEXTURES
PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_PATCHES

define PCSX2_CROSSHAIRS
	mkdir -p $(TARGET_DIR)/usr/pcsx2/bin/resources/crosshairs
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/pcsx2/crosshairs/ \
        $(TARGET_DIR)/usr/pcsx2/bin/resources/
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_CROSSHAIRS

$(eval $(cmake-package))
