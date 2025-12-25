################################################################################
#
# libretro-dolphin
#
################################################################################
# Version: Commits on Dec 24, 2025
LIBRETRO_DOLPHIN_VERSION = ee45d31871212384cc1db3e9126ebcdfbf526613
LIBRETRO_DOLPHIN_SITE = $(call github,libretro,dolphin,$(LIBRETRO_DOLPHIN_VERSION))
LIBRETRO_DOLPHIN_SITE_METHOD = git
LIBRETRO_DOLPHIN_GIT_SUBMODULES = YES
LIBRETRO_DOLPHIN_LICENSE = GPLv2
LIBRETRO_DOLPHIN_DEPENDENCIES = libevdev fmt bluez5_utils retroarch pugixml libenet libcurl hidapi

LIBRETRO_DOLPHIN_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_DOLPHIN_CONF_OPTS = -DLIBRETRO=ON \
                             -DLINUX=ON \
                             -DENABLE_NOGUI=OFF \
                             -DENABLE_QT=OFF \
                             -DENABLE_TESTS=OFF \
                             -DUSE_DISCORD_PRESENCE=OFF \
                             -DUSE_SYSTEM_XXHASH=OFF \
                             -DUSE_SYSTEM_SPNG=OFF \
                             -DBUILD_SHARED_LIBS=OFF \
                             -DCMAKE_BUILD_TYPE=Release \
                             -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -fpermissive"

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    LIBRETRO_DOLPHIN_DEPENDENCIES += xserver_xorg-server
    LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=ON
else
    LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=OFF
endif

define LIBRETRO_DOLPHIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dolphin_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/dolphin_libretro.so
endef

define LIBRETRO_DOLPHIN_SYS_FOLDER
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/dolphin-emu/Sys
	cp -r $(@D)/Data/Sys/* $(TARGET_DIR)/usr/share/batocera/datainit/bios/dolphin-emu/Sys
endef

LIBRETRO_DOLPHIN_POST_INSTALL_TARGET_HOOKS += LIBRETRO_DOLPHIN_SYS_FOLDER

$(eval $(cmake-package))
