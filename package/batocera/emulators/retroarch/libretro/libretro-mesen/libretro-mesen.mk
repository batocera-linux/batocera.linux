################################################################################
#
# MESEN
#
################################################################################
# Version.: Commits on Oct 07, 2020
LIBRETRO_MESEN_VERSION = aa2f444467ab92b8f4faaffbf013c728e79e2d8a
LIBRETRO_MESEN_SITE = $(call github,libretro,Mesen,$(LIBRETRO_MESEN_VERSION))

define LIBRETRO_MESEN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen_libretro.so
endef

$(eval $(generic-package))
