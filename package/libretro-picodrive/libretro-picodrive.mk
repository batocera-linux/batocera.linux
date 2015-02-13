################################################################################
#
# libretro-picodrive
#
################################################################################
LIBRETRO_PICODRIVE_VERSION = master
LIBRETRO_PICODRIVE_SITE = $(call github,libretro,picodrive,$(LIBRETRO_PICODRIVE_VERSION))
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng sdl

PLATFORM =
ifeq ($(BR2_ARM_CPU_ARMV6),y)
        PLATFORM = armv6
endif

ifeq ($(BR2_cortex_a7),y)
        PLATFORM = armv7
endif

ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),hard)
        PLATFORM += hardfloat
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        PLATFORM += neon
endif

define LIBRETRO_PICODRIVE_CONFIGURE_CMDS
	rm -rf $(@D)/picodrive
	git -C $(@D) clone https://github.com/libretro/picodrive
	#cp -r $(@D)/../picodrivegithub/.git $(@D)/
	git -C $(@D)/picodrive submodule update --init
	##( cd $(@D)/picodrive && \
        ##CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" CFLAGS="$(TARGET_CFLAGS)" \
	##./configure )
endef


define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/picodrive/cpu/cyclone CONFIG_FILE=$(@D)/picodrive/cpu/cyclone_config.h	
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" -C  $(@D)/picodrive -f Makefile.libretro platform="$(PLATFORM) armasm"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef
#LIBRETRO_PICODRIVE_PRE_CONFIGURE_HOOKS +=  LIBRETRO_PICODRIVE_GITHUBHACK
$(eval $(generic-package))
#$(eval $(autotools-package))

