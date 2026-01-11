################################################################################
#
# libretro-ep128emu
#
################################################################################
LIBRETRO_EP128EMU_VERSION = core_v1.2.11
LIBRETRO_EP128EMU_SITE = $(call github,libretro,ep128emu-core,$(LIBRETRO_EP128EMU_VERSION))
LIBRETRO_EP128EMU_LICENSE = GPLv2
LIBRETRO_EP128EMU_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_EP128EMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" \
		-C $(@D)/libretro \
		platform="$(LIBRETRO_EP128EMU_PLATFORM)"
endef

define LIBRETRO_EP128EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/ep128emu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu_libretro.so
endef

$(eval $(generic-package))
