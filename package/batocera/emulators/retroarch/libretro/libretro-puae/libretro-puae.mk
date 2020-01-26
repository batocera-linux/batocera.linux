################################################################################
#
# PUAE
#
################################################################################
# Version.: Commits on Jan 23, 2020
LIBRETRO_PUAE_VERSION = 1da3fa0b82acf1d77d302b3f055d75cb02299f97
LIBRETRO_PUAE_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE_VERSION))
LIBRETRO_PUAE__LICENSE = GPLv2

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PUAEPLATFORM=rpi
else
	PUAEPLATFORM=unix
	ifeq ($(BR2_ARM_CPU_HAS_ARM),y)
		PUAEPLATFLAGS=-DARM  -marm
	endif
	ifeq ($(BR2_aarch64),y)
		PUAEPLATFLAGS=-DAARCH64
	endif
endif

define LIBRETRO_PUAE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) \
		CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(PUAEPLATFORM)" platflags="$(PUAEPLATFLAGS)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
