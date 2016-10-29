################################################################################
#
# UAE
#
################################################################################
LIBRETRO_UAE_VERSION = 7cbc2304d064cf58455bc4bdf589cb3fd51865a8
LIBRETRO_UAE_SITE = $(call github,libretro,libretro-uae,master)

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	UAEPLATFORM=rpi
else
	UAEPLATFORM=unix
	ifeq ($(BR2_ARM_CPU_HAS_ARM),y)
		UAEPLATFLAGS=-DARM  -marm
	endif
	ifeq ($(BR2_aarch64),y)
		UAEPLATFLAGS=-DAARCH64
	endif
endif

define LIBRETRO_UAE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(UAEPLATFORM)" platflags="$(UAEPLATFLAGS)"
endef

define LIBRETRO_UAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
