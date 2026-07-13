################################################################################
#
# libretro-ep128emu-core
#
################################################################################

LIBRETRO_EP128EMU_CORE_VERSION = core_v1.2.11
LIBRETRO_EP128EMU_CORE_SITE = $(call github,libretro,ep128emu-core,$(LIBRETRO_EP128EMU_CORE_VERSION))
LIBRETRO_EP128EMU_CORE_SITE_METHOD = tar
LIBRETRO_EP128EMU_CORE_LICENSE = GPL-2.0
LIBRETRO_EP128EMU_CORE_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_EP128EMU_CORE_EMULATOR_INFO = ep128emu-core.libretro.core.yml

define LIBRETRO_EP128EMU_CORE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CC="$(TARGET_CC)" \
		CXX="$(TARGET_CXX)" \
		-C $(@D) \
		platform="unix"
endef

define LIBRETRO_EP128EMU_CORE_INSTALL_TARGET_CMDS
	$(INSTALL) -D \
		$(@D)/ep128emu_core_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu-core_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
