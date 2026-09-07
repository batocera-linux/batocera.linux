################################################################################
#
# armsx2
#
################################################################################
# Version: Commits on September 05, 2026
ARMSX2_VERSION = a0954c09f7a482ff2dcab359d8c0e64d77ab3e1a
ARMSX2_SITE = https://github.com/ARMSX2/ARMSX2.git
ARMSX2_SITE_METHOD = git
ARMSX2_GIT_SUBMODULES = YES
ARMSX2_LICENSE = GPLv3
ARMSX2_LICENSE_FILE = COPYING.GPLv3
ARMSX2_EMULATOR_INFO = armsx2.emulator.yml

ARMSX2_SUPPORTS_IN_SOURCE_BUILD = NO

ARMSX2_DEPENDENCIES += alsa-lib ecm fmt freetype host-clang host-libcurl kddockwidgets
ARMSX2_DEPENDENCIES += libaio libbacktrace libcurl libgtk3 libpcap libpng libsamplerate
ARMSX2_DEPENDENCIES += libsoundtouch plutosvg portaudio qt6base qt6svg qt6tools
ARMSX2_DEPENDENCIES += rapidyaml shaderc sdl3 webp wxwidgets xorgproto yaml-cpp zlib

# Use clang for performance
ARMSX2_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
ARMSX2_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
ARMSX2_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++"
ARMSX2_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -march=armv8-a -moutline-atomics"
ARMSX2_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -march=armv8-a -moutline-atomics -Wno-c++11-narrowing -Wno-narrowing"
ARMSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
ARMSX2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
ARMSX2_CONF_OPTS += -DENABLE_TESTS=OFF
ARMSX2_CONF_OPTS += -DUSE_SYSTEM_LIBS=AUTO
ARMSX2_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON
ARMSX2_CONF_OPTS += -DHOST_PAGE_SIZE=4096
ARMSX2_CONF_OPTS += -DHOST_CACHE_LINE_SIZE=64

# below may not be needed for newer versions
define ARMSX2_FIX_WHOLE_ARCHIVE
	find $(@D) -name "CMakeLists.txt" -exec sed -i 's|.[<]LINK_LIBRARY:WHOLE_ARCHIVE,\([^>]*\)>|-Wl,--whole-archive \1 -Wl,--no-whole-archive|g' {} +
endef
ARMSX2_PRE_CONFIGURE_HOOKS += ARMSX2_FIX_WHOLE_ARCHIVE

ifeq ($(BR2_PACKAGE_XORG7),y)
    ARMSX2_CONF_OPTS += -DX11_API=ON
else
    ARMSX2_CONF_OPTS += -DX11_API=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
    ARMSX2_CONF_OPTS += -DWAYLAND_API=ON
else
    ARMSX2_CONF_OPTS += -DWAYLAND_API=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    ARMSX2_CONF_OPTS += -DUSE_OPENGL=ON
else
    ARMSX2_CONF_OPTS += -DUSE_OPENGL=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    ARMSX2_CONF_OPTS += -DUSE_VULKAN=ON
else
    ARMSX2_CONF_OPTS += -DUSE_VULKAN=OFF
endif

define ARMSX2_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/buildroot-build/bin/armsx2-qt \
        $(TARGET_DIR)/usr/armsx2/bin/armsx2-qt
	cp -pr  $(@D)/bin/resources $(TARGET_DIR)/usr/armsx2/bin/
    cp -pr  $(@D)/buildroot-build/bin/translations $(TARGET_DIR)/usr/armsx2/bin/
    # use our SDL config
    rm $(TARGET_DIR)/usr/armsx2/bin/resources/game_controller_db.txt
endef

# Download and copy PCSX2 patches.zip to BIOS folder (ARMSX2 shares the PS2 game database)
define ARMSX2_PATCHES
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/ps2
    $(HOST_DIR)/bin/curl -L \
        https://github.com/PCSX2/pcsx2_patches/releases/download/latest/patches.zip -o \
        $(TARGET_DIR)/usr/share/batocera/datainit/bios/ps2/patches.zip
endef

ARMSX2_POST_INSTALL_TARGET_HOOKS += ARMSX2_PATCHES

$(eval $(cmake-package))
$(eval $(emulator-info-package))
