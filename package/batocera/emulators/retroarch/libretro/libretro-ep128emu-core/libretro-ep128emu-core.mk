################################################################################
#
# libretro-ep128emu-core
#
################################################################################

LIBRETRO_EP128EMU_VERSION = core_v1.2.11
LIBRETRO_EP128EMU_SITE = $(call github,libretro,ep128emu-core,$(LIBRETRO_GEARCOLECO_VERSION))
LIBRETRO_EP128EMU_SITE_METHOD = tar
LIBRETRO_EP128EMU_LICENSE = GPL-2.0
LIBRETRO_EP128EMU_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_EP128EMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CC="$(TARGET_CC)" \
		CXX="$(TARGET_CXX)" \
		-C $(@D) \
		platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_EP128EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D \
		$(@D)/ep128emu-core_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu-core_libretro.so
endef

$(eval $(generic-package))
