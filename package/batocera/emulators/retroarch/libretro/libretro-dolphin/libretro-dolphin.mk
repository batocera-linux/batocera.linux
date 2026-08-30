################################################################################
#
# libretro-dolphin
#
################################################################################
# Version: Commits on Aug 27, 2026
LIBRETRO_DOLPHIN_VERSION = c16d4254d1341f0fb7d564498cbf3ac7ac236eae
LIBRETRO_DOLPHIN_SITE = https://github.com/libretro/dolphin.git
LIBRETRO_DOLPHIN_SITE_METHOD = git
LIBRETRO_DOLPHIN_GIT_SUBMODULES = YES
LIBRETRO_DOLPHIN_LICENSE = GPLv2
LIBRETRO_DOLPHIN_DEPENDENCIES = libevdev fmt bluez5_utils retroarch pugixml libenet libcurl
LIBRETRO_DOLPHIN_EMULATOR_INFO = dolphin.libretro.core.yml

LIBRETRO_DOLPHIN_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_DOLPHIN_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release \
                             -DBUILD_SHARED_LIBS=OFF \
                             -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -fpermissive" \
                             -DLIBRETRO=ON \
                             -DLINUX=ON \
                             -DENABLE_NOGUI=OFF \
                             -DENABLE_QT=OFF \
                             -DENABLE_TESTS=OFF \
                             -DUSE_DISCORD_PRESENCE=OFF \
                             -DUSE_SYSTEM_XXHASH=OFF \
                             -DUSE_SYSTEM_SPNG=OFF \
                             -DUSE_SYSTEM_HIDAPI=OFF

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
$(eval $(emulator-info-package))
