################################################################################
#
# libretro-mgba
#
################################################################################

LIBRETRO_MGBA_VERSION = 0.9.3
LIBRETRO_MGBA_SITE = $(call github,mgba-emu,mgba,$(LIBRETRO_MGBA_VERSION))
LIBRETRO_MGBA_LICENSE = MPLv2.0

LIBRETRO_MGBA_DEPENDENCIES = libzip libpng zlib

LIBRETRO_MGBA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DBUILD_LIBRETRO=ON \
    -DSKIP_LIBRARY=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF \
	-DUSE_GDB_STUB=OFF -DUSE_SQLITE3=OFF -DUSE_DEBUGGERS=OFF -DUSE_EDITLINE=OFF \
	-DUSE_EPOXY=OFF

ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    LIBRETRO_MGBA_CONF_OPTS += -DBUILD_GLES3=ON -DBUILD_GLES2=OFF
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    LIBRETRO_MGBA_CONF_OPTS += -DBUILD_GLES2=ON -DBUILD_GLES3=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    LIBRETRO_MGBA_CONF_OPTS += -DBUILD_GL=ON
else
    LIBRETRO_MGBA_CONF_OPTS += -DBUILD_GL=OFF
endif

define LIBRETRO_MGBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mgba_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mgba_libretro.so
endef

$(eval $(cmake-package))
