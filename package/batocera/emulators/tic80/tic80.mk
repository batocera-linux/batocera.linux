################################################################################
#
# tic80
#
################################################################################
# Version: Stable release v1.1.2837 (October 22, 2024)
TIC80_VERSION = v1.1.2837
TIC80_SITE = https://github.com/nesbox/TIC-80.git
TIC80_SITE_METHOD = git
TIC80_GIT_SUBMODULES = YES
TIC80_LICENSE = MIT
TIC80_LICENSE_FILES = LICENSE

TIC80_DEPENDENCIES = sdl2 host-pkgconf zlib libcurl

TIC80_CONF_OPTS += -DBUILD_LIBRETRO=OFF
TIC80_CONF_OPTS += -DBUILD_PLAYER=OFF
TIC80_CONF_OPTS += -DBUILD_SOKOL=OFF
TIC80_CONF_OPTS += -DBUILD_SDL=ON
TIC80_CONF_OPTS += -DBUILD_DEMO_CARTS=OFF

ifeq ($(BR2_PACKAGE_LIBGLES),y)
TIC80_CONF_OPTS += -DBUILD_WITH_GLES=ON
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
TIC80_DEPENDENCIES += alsa-lib
endif

ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
TIC80_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-latomic
endif

define TIC80_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/tic80 $(TARGET_DIR)/usr/bin/tic80
endef

$(eval $(cmake-package))
