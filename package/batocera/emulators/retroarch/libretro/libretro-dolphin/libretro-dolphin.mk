################################################################################
#
# libretro-dolphin
#
################################################################################
# Version: Commits on Jun 23, 2022
LIBRETRO_DOLPHIN_VERSION = 6ebaa94082f516cd19f31432ff4779ff3685076c
LIBRETRO_DOLPHIN_SITE = https://github.com/libretro/dolphin
LIBRETRO_DOLPHIN_SITE_METHOD=git
LIBRETRO_DOLPHIN_GIT_SUBMODULES=YES
LIBRETRO_DOLPHIN_LICENSE = GPLv2
LIBRETRO_DOLPHIN_DEPENDENCIES = retroarch libevdev fmt bluez5_utils

LIBRETRO_DOLPHIN_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_DOLPHIN_CONF_OPTS = -DUSE_DISCORD_PRESENCE=OFF -DLIBRETRO=ON \
    -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
LIBRETRO_DOLPHIN_DEPENDENCIES += xserver_xorg-server
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_EGL=OFF
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
LIBRETRO_DOLPHIN_CONF_OPTS += -DCMAKE_SHARED_LINKER_FLAGS="-lmali_hook -Wl,--whole-archive -lmali_hook_injector -Wl,--no-whole-archive -lmali"
LIBRETRO_DOLPHIN_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lmali_hook -Wl,--whole-archive -lmali_hook_injector -Wl,--no-whole-archive -lmali"
endif

define LIBRETRO_DOLPHIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dolphin_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/dolphin_libretro.so
endef

$(eval $(cmake-package))
