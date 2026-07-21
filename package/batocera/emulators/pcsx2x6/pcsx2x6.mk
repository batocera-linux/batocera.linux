################################################################################
#
# pcsx2x6
#
################################################################################
# Version: Commits on Jul 20, 2026
PCSX2X6_VERSION = 758326a085f2029cef4df08e8b23a3e574cfd085
PCSX2X6_SITE = https://github.com/PS2Homebrew-arcade/pcsx2x6.git
PCSX2X6_SITE_METHOD = git
PCSX2X6_GIT_SUBMODULES = YES
PCSX2X6_LICENSE = GPLv3
PCSX2X6_LICENSE_FILE = COPYING.GPLv3
PCSX2X6_EMULATOR_INFO = pcsx2x6.emulator.yml

PCSX2X6_SUPPORTS_IN_SOURCE_BUILD = NO

PCSX2X6_DEPENDENCIES += alsa-lib ecm fmt freetype host-clang host-libcurl kddockwidgets
PCSX2X6_DEPENDENCIES += libaio libbacktrace libcurl libgtk3 libpcap libpng libsamplerate
PCSX2X6_DEPENDENCIES += libsoundtouch plutosvg portaudio qt6base qt6svg qt6tools
PCSX2X6_DEPENDENCIES += rapidyaml shaderc sdl3 webp wxwidgets xorgproto yaml-cpp zlib

# Use clang for performance
PCSX2X6_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
PCSX2X6_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
PCSX2X6_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++"

ifeq ($(BR2_aarch64),y)
PCSX2X6_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS)"
PCSX2X6_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -Wno-c++11-narrowing -Wno-narrowing"
endif

PCSX2X6_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PCSX2X6_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
PCSX2X6_CONF_OPTS += -DENABLE_TESTS=OFF
PCSX2X6_CONF_OPTS += -DUSE_SYSTEM_LIBS=AUTO
# The following flag is misleading and *needed* ON to avoid doing -march=native
PCSX2X6_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON

# below may not be needed for newer versions
define PCSX2X6_FIX_WHOLE_ARCHIVE
	find $(@D) -name "CMakeLists.txt" -exec sed -i 's|.[<]LINK_LIBRARY:WHOLE_ARCHIVE,\([^>]*\)>|-Wl,--whole-archive \1 -Wl,--no-whole-archive|g' {} +
endef
PCSX2X6_PRE_CONFIGURE_HOOKS += PCSX2X6_FIX_WHOLE_ARCHIVE

ifeq ($(BR2_PACKAGE_XORG7),y)
    PCSX2X6_CONF_OPTS += -DX11_API=ON
else
    PCSX2X6_CONF_OPTS += -DX11_API=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
    PCSX2X6_CONF_OPTS += -DWAYLAND_API=ON
else
    PCSX2X6_CONF_OPTS += -DWAYLAND_API=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    PCSX2X6_CONF_OPTS += -DUSE_OPENGL=ON
else
    PCSX2X6_CONF_OPTS += -DUSE_OPENGL=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    PCSX2X6_CONF_OPTS += -DUSE_VULKAN=ON
else
    PCSX2X6_CONF_OPTS += -DUSE_VULKAN=OFF
endif

define PCSX2X6_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/buildroot-build/bin/pcsx2-qt \
        $(TARGET_DIR)/usr/pcsx2x6/bin/pcsx2x6-qt
	cp -pr  $(@D)/bin/resources $(TARGET_DIR)/usr/pcsx2x6/bin/
    cp -pr  $(@D)/buildroot-build/bin/translations $(TARGET_DIR)/usr/pcsx2x6/bin/
    # use our SDL config
    rm $(TARGET_DIR)/usr/pcsx2x6/bin/resources/game_controller_db.txt
endef

# Download and copy PCSX2X6 patches.zip to BIOS folder
define PCSX2X6_PATCHES
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/namco2x6
    $(HOST_DIR)/bin/curl -L \
        https://github.com/PS2Homebrew-arcade/pcsx2x6_patches/releases/download/latest/patches.zip -o \
        $(TARGET_DIR)/usr/share/batocera/datainit/bios/namco2x6/patches.zip
endef

PCSX2X6_POST_INSTALL_TARGET_HOOKS += PCSX2X6_PATCHES

define PCSX2X6_CROSSHAIRS
	mkdir -p $(TARGET_DIR)/usr/pcsx2x6/bin/resources/crosshairs
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/pcsx2x6/crosshairs/ \
        $(TARGET_DIR)/usr/pcsx2x6/bin/resources/
endef

PCSX2X6_POST_INSTALL_TARGET_HOOKS += PCSX2X6_CROSSHAIRS

$(eval $(cmake-package))
$(eval $(emulator-info-package))
