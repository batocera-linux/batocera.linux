################################################################################
#
# libretro-picodrive
#
################################################################################
LIBRETRO_PICODRIVE_VERSION = f0a3d0dc4bd9060eb6bfdb16fb20dbb80a9e6ae9
LIBRETRO_PICODRIVE_SITE = $(call github,libretro,picodrive,$(LIBRETRO_PICODRIVE_VERSION))
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng sdl

define LIBRETRO_PICODRIVE_CONFIGURE_CMDS
	rm -rf $(@D)/picodrive
	git -C $(@D) clone https://github.com/libretro/picodrive
	#git -C $(@D) checkout $(LIBRETRO_PICODRIVE_VERSION)
	#cp -r $(@D)/../picodrivegithub/.git $(@D)/
	git -C $(@D)/picodrive submodule update --init
	##( cd $(@D)/picodrive && \
        ##CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" CFLAGS="$(TARGET_CFLAGS)" \
	##./configure )
endef

PICOPLATFORM=$(LIBRETRO_PLATFORM)

# RPI 0 and 1
ifeq ($(BR2_arm1176jzf_s),y)
  PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
endif

# RPI 2 and 3
ifeq ($(BR2_cortex_a7),y)
  PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
endif
ifeq ($(BR2_cortex_a8),y)
  PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
endif

# odroid xu4
ifeq ($(BR2_cortex_a15),y)
  PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
endif

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/picodrive/cpu/cyclone CONFIG_FILE=$(@D)/picodrive/cpu/cyclone_config.h	
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" -C  $(@D)/picodrive -f Makefile.libretro platform="$(PICOPLATFORM)"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef
#LIBRETRO_PICODRIVE_PRE_CONFIGURE_HOOKS +=  LIBRETRO_PICODRIVE_GITHUBHACK
$(eval $(generic-package))
#$(eval $(autotools-package))

