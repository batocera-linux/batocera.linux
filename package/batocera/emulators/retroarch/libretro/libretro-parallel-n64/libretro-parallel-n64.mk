################################################################################
#
# PARALLEL_N64
#
################################################################################

# for rpi2, rpi3 and odroid because the next commit breaks and has lost performance.
# Version.: Commits on Aug 8, 2018 
LIBRETRO_PARALLEL_N64_VERSION = ab155da18068f638e5ace2e5e6f7387bddc3511b
LIBRETRO_PARALLEL_N64_SITE = $(call github,libretro,parallel-n64,$(LIBRETRO_PARALLEL_N64_VERSION))
LIBRETRO_PARALLEL_N64_LICENSE="GPLv2"

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
       LIBRETRO_PARALLEL_N64_DEPENDENCIES += rpi-userland
endif

LIBRETRO_PARALLEL_N64_SUPP_OPT=

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=rpi3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=odroid-ODROID-XU3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_C2),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=FORCE_GLES=1 ARCH=aarch64
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=FORCE_GLES=1 ARCH=aarch64
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=FORCE_GLES=1 ARCH=aarch64
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_x86_i586),y)
       LIBRETRO_PARALLEL_N64_SUPP_OPT=ARCH=i386
       LIBRETRO_PARALLEL_N64_PLATFORM=unix
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
       LIBRETRO_PARALLEL_N64_PLATFORM=rockpro64
else
       LIBRETRO_PARALLEL_N64_PLATFORM=$(LIBRETRO_PLATFORM)
endif

define LIBRETRO_PARALLEL_N64_BUILD_CMDS
       CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
              $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PARALLEL_N64_PLATFORM)" $(LIBRETRO_PARALLEL_N64_SUPP_OPT)
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
