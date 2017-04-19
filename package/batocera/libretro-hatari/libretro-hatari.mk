################################################################################
#
# HATARI
#
################################################################################
LIBRETRO_HATARI_VERSION = e99678be2123eed4875586d2e28790d85273226e
LIBRETRO_HATARI_SITE = $(call github,libretro,hatari,$(LIBRETRO_HATARI_VERSION))
LIBRETRO_HATARI_DEPENDENCIES = libcapsimage

define LIBRETRO_HATARI_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" ASFLAGS="$(TARGET_ASFLAGS)" PLATFLAGS="$(TARGET_PLATFLAGS)" SHARED="$(TARGET_SHARED)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro

endef

define LIBRETRO_HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/hatari_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/hatari_libretro.so
endef

define LIBRETRO_HATARI_PRE_PATCH_FIXUP
	$(SED) 's/\r//g' $(@D)/Makefile.libretro
endef

LIBRETRO_HATARI_PRE_PATCH_HOOKS += LIBRETRO_HATARI_PRE_PATCH_FIXUP

$(eval $(generic-package))
