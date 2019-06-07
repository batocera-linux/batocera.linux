################################################################################
#
# DOSBOX
#
################################################################################
# Version.: Commits on Mar 20, 2019
LIBRETRO_DOSBOX_VERSION = 2aa0bd13b372956b2fe989ca5e9d8e45f75fb44d
LIBRETRO_DOSBOX_SITE = $(call github,libretro,dosbox-libretro,$(LIBRETRO_DOSBOX_VERSION))
LIBRETRO_DOSBOX_LICENSE = GPLv2

ifeq ($(BR2_arm),y)
	LIBRETRO_DOSBOX_CONF_OPTS = WITH_DYNAREC=arm
endif

define LIBRETRO_DOSBOX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile.libretro 
endef

define LIBRETRO_DOSBOX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dosbox_libretro.so \
	  $(TARGET_DIR)/usr/lib/libretro/dosbox_libretro.so
endef

$(eval $(generic-package))
