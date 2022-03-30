
################################################################################
#
# libretro-gpsp
#
################################################################################
# Version: Commits on Jan 20, 2022
LIBRETRO_GPSP_VERSION = e554360dd3ed283696fc607877024a219248b735
LIBRETRO_GPSP_SITE = $(call github,libretro,gpsp,$(LIBRETRO_GPSP_VERSION))
LIBRETRO_GPSP_LICENSE = GPLv2

LIBRETRO_GPSP_PLATFORM = unix

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_GPSP_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_GPSP_PLATFORM = rpi2
endif

define LIBRETRO_GPSP_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform=$(LIBRETRO_GPSP_PLATFORM) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_GPSP_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_GPSP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gpsp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gpsp_libretro.so
endef

$(eval $(generic-package))
