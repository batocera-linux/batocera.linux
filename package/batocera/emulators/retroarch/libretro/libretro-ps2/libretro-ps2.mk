################################################################################
#
# libretro-ps2
#
################################################################################
# Version: Commits on Aug 29, 2026
LIBRETRO_PS2_VERSION = 2dac3458788179b299d597863f500b26aaddb50d
LIBRETRO_PS2_SITE = https://github.com/libretro/ps2.git
LIBRETRO_PS2_SITE_METHOD = git
LIBRETRO_PS2_GIT_SUBMODULES = YES
LIBRETRO_PS2_LICENSE = GPLv2
LIBRETRO_PS2_DEPENDENCIES = libaio xz host-xxd retroarch
LIBRETRO_PS2_EMULATOR_INFO = pcsx2.libretro.core.yml
LIBRETRO_PS2_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_PS2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_PS2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_PS2_CONF_OPTS += -DLIBRETRO=ON
LIBRETRO_PS2_CONF_OPTS += -DBUILD_REGRESS=OFF
LIBRETRO_PS2_CONF_OPTS += -DBUILD_TOOLS=OFF
LIBRETRO_PS2_CONF_OPTS += -DCMAKE_POLICY_VERSION_MINIMUM=3.5
LIBRETRO_PS2_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -Wno-error=implicit-function-declaration"
LIBRETRO_PS2_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -Wno-error=implicit-function-declaration"

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    LIBRETRO_PS2_CONF_OPTS += -DUSE_OPENGL=ON
else
    LIBRETRO_PS2_CONF_OPTS += -DUSE_OPENGL=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    LIBRETRO_PS2_CONF_OPTS += -DUSE_VULKAN=ON
else
    LIBRETRO_PS2_CONF_OPTS += -DUSE_VULKAN=OFF
endif

# below may not be needed for newer versions
define LIBRETRO_PS2_FIX_WHOLE_ARCHIVE
	find $(@D) -name "CMakeLists.txt" -exec sed -i 's|.[<]LINK_LIBRARY:WHOLE_ARCHIVE,\([^>]*\)>|-Wl,--whole-archive \1 -Wl,--no-whole-archive|g' {} +
endef
LIBRETRO_PS2_PRE_CONFIGURE_HOOKS += LIBRETRO_PS2_FIX_WHOLE_ARCHIVE

define LIBRETRO_PS2_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/bin/pcsx2_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx2_libretro.so
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/pcsx2/resources
    cp -f $(@D)/bin/resources/GameIndex.yaml \
        $(TARGET_DIR)/usr/share/batocera/datainit/bios/pcsx2/resources
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))