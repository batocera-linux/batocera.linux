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
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
	    $(@D)/src/os/libretro -f Makefile platform="$(LIBRETRO_EP128EMU_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_EP128EMU_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_EP128EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/os/libretro/ep128emu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu_libretro.so
endef

$(eval $(generic-package))
