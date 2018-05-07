################################################################################
#
# PARALLEL_N64
#
################################################################################
# Version.: Commits on Apr 22, 2018
LIBRETRO_PARALLEL_N64_VERSION = 55c4ee7007f0eb4ab8e66dced66de406ff96a10c
LIBRETRO_PARALLEL_N64_SITE = $(call github,libretro,parallel-n64,$(LIBRETRO_PARALLEL_N64_VERSION))

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
       LIBRETRO_PARALLEL_N64_DEPENDENCIES += rpi-userland
endif

LIBRETRO_PARALLEL_N64_SUPP_OPT=

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=rpi3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=rpi2
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_XU4)$(BR2_PACKAGE_RECALBOX_TARGET_LEGACYXU4),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=odroid-ODROID-XU3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_C2),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=FORCE_GLES=1 ARCH=aarch64
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S905),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=FORCE_GLES=1 ARCH=aarch64
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S912),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=FORCE_GLES=1 ARCH=aarch64
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_x86_i586),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=ARCH=i386
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else
       LIBRETRO_PARALLEL_N64_PLATFORM=$(LIBRETRO_PLATFORM)
endif

define LIBRETRO_PARALLEL_N64_BUILD_CMDS
       CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PARALLEL_N64_PLATFORM)" $(LIBRETRO_PARALLEL_N64_SUPP_OPT)
endef

define LIBRETRO_PARALLEL_N64_INSTALL_TARGET_CMDS
       $(INSTALL) -D $(@D)/parallel_n64_libretro.so \
               $(TARGET_DIR)/usr/lib/libretro/parallel_n64_libretro.so
endef

define PARALLEL_N64_CROSS_FIXUP
       $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/Makefile
       $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/Makefile
endef

PARALLEL_N64_PRE_CONFIGURE_HOOKS += PARALLEL_N64_FIXUP

$(eval $(generic-package))
