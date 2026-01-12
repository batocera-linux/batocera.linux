################################################################################
#
# libretro-ep128emu
#
################################################################################

LIBRETRO_EP128EMU_VERSION = 812dd1b35225b64d9392a3e21de28c3a5861ddf7
LIBRETRO_EP128EMU_SITE = $(call github,libretro,ep128emu-core,$(LIBRETRO_EP128EMU_VERSION))
LIBRETRO_EP128EMU_LICENSE = GPL-2.0
LIBRETRO_EP128EMU_DEPENDENCIES += retroarch

LIBRETRO_EP128EMU_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_EP128EMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CC="$(TARGET_CC)" \
		CXX="$(TARGET_CXX)" \
		-C $(@D)/libretro \
		platform="$(LIBRETRO_EP128EMU_PLATFORM)"
endef

define LIBRETRO_EP128EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D \
		$(@D)/src/libretro/ep128emu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu_libretro.so
endef

$(eval $(generic-package))
