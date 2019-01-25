################################################################################
#
# MAME2016
#
################################################################################
# Version.: Commits on Aug 10, 2018
LIBRETRO_MAME2016_VERSION = e06d731644217f46bf5a7613222632d41a327f93
LIBRETRO_MAME2016_SITE = $(call github,libretro,mame2016-libretro,$(LIBRETRO_MAME2016_VERSION))

# x86
ifeq ($(BR2_x86_i586),y)
	LIBRETRO_MAME2016_PLATFORM = PTR64=0
endif

# x86_64
ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME2016_PLATFORM = PTR64=1
endif

define LIBRETRO_MAME2016_BUILD_CMDS
        mkdir -p "$(@D)/3rdparty/genie/build/gmake.linux/obj/Release/src/host"
	mkdir -p "$(@D)/build/gmake/libretro/obj/x64/libretro/src/osd/retro"
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile.libretro $(LIBRETRO_MAME2016_PLATFORM) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MAME2016_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2016_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame0174_libretro.so
endef

$(eval $(generic-package))
