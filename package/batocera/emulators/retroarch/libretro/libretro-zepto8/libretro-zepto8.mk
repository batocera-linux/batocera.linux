################################################################################
#
# zepto8 - PICO-8 emulator
#
################################################################################
# Version.: Commits on Oct 20, 2020
LIBRETRO_ZEPTO8_VERSION = 486522b34574f60e6963cdcfbed6c0cdd600e81c
LIBRETRO_ZEPTO8_SITE = git://github.com/samhocevar/zepto8.git
LIBRETRO_ZEPTO8_SITE_METHOD=git
LIBRETRO_ZEPTO8_GIT_SUBMODULES=YES
LIBRETRO_ZEPTO8_LICENSE = MIT
LIBRETRO_ZEPTO8_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_ZEPTO8_CONFIGURE_CMDS
    cd $(@D); ./bootstrap; autoconf; ./configure --prefix=$(@D)/output --enable-LOL_USE_SDL_TRUE
endef
#    --enable-LOL_USE_SDL_TRUE

LIBRETRO_ZEPTO8_CONF_OPTS += -D

define LIBRETRO_ZEPTO8_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_TIC80_PLATFORM)"
endef

define LIBRETRO_ZEPTO8_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/.libs/libretro-zepto8.so.0.0.0 $(TARGET_DIR)/usr/lib/libretro/zepto8_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/pico8/
	$(INSTALL) -D $(@D)/src/pico8/bios.p8 $(TARGET_DIR) $(TARGET_DIR)/usr/share/batocera/datainit/bios/pico8/
	$(INSTALL) -D $(@D)/src/unz8.p8 $(TARGET_DIR) $(TARGET_DIR)/usr/share/batocera/datainit/bios/pico8/
endef

$(eval $(autotools-package))
$(eval $(host-autotools-package))
