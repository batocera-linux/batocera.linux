################################################################################
#
# PUAE
#
################################################################################
# Version.: Commits on Feb 04, 2020
LIBRETRO_PUAE_VERSION = 167f4fdb079ed41f7be1874b90d9c2ec6adc9ccb
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
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(PUAEPLATFORM)" platflags="$(PUAEPLATFLAGS)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
