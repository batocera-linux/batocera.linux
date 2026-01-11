################################################################################
#
# libretro-ep128emu
#
################################################################################

LIBRETRO_EP128EMU_VERSION = master
LIBRETRO_EP128EMU_SITE = https://github.com/libretro/ep128emu-core.git
LIBRETRO_EP128EMU_SITE_METHOD = git
LIBRETRO_EP128EMU_LICENSE = GPLv2
LIBRETRO_EP128EMU_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_EP128EMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" \
		-C $(@D)/src/libretro \
		platform="$(LIBRETRO_EP128EMU_PLATFORM)"
endef

define LIBRETRO_EP128EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D \
		$(@D)/src/libretro/ep128emu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu_libretro.so
endef

$(eval $(generic-package))
