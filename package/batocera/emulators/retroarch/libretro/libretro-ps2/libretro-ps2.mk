################################################################################
#
# libretro-ps2
#
################################################################################
# Version: Commits on Jul 4, 2025
LIBRETRO_PS2_VERSION = f8c9740897cbba47ee5ecda9f1c34d73daf81379
LIBRETRO_PS2_SITE = https://github.com/libretro/ps2.git
LIBRETRO_PS2_SITE_METHOD = git
LIBRETRO_PS2_GIT_SUBMODULES = YES
LIBRETRO_PS2_LICENSE = GPLv2
LIBRETRO_PS2_DEPENDENCIES = libaio xz host-xxd retroarch

LIBRETRO_PS2_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_PS2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_PS2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_PS2_CONF_OPTS += -DLIBRETRO=ON
LIBRETRO_PS2_CONF_OPTS += -DBUILD_REGRESS=OFF
LIBRETRO_PS2_CONF_OPTS += -DBUILD_TOOLS=OFF

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

define LIBRETRO_PS2_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/bin/pcsx2_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx2_libretro.so
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/pcsx2/resources
    cp -f $(@D)/bin/resources/GameIndex.yaml \
        $(TARGET_DIR)/usr/share/batocera/datainit/bios/pcsx2/resources
endef

$(eval $(cmake-package))
