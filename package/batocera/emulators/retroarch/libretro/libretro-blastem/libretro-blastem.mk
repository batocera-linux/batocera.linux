################################################################################
#
# libretro-blastem
#
################################################################################
# Version: Commits on Jul 26, 2022
LIBRETRO_BLASTEM_VERSION = 277e4a62668597d4f59cadda1cbafb844f981d45
LIBRETRO_BLASTEM_SITE = $(call github,libretro,blastem,$(LIBRETRO_BLASTEM_VERSION))
LIBRETRO_BLASTEM_LICENSE = GPLv3

LIBRETRO_BLASTEM_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
LIBRETRO_BLASTEM_EXTRAOPTS=CPU=x86_64
else  ifeq ($(BR2_x86_i686),y)
LIBRETRO_BLASTEM_EXTRAOPTS=CPU=i686
endif

define LIBRETRO_BLASTEM_BUILD_CMDS
    $(SED) "s+CPU:=i686+CPU?=i686+g" $(@D)/Makefile
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) libblastem.so $(LIBRETRO_BLASTEM_EXTRAOPTS)
endef

define LIBRETRO_BLASTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libblastem.so \
		$(TARGET_DIR)/usr/lib/libretro/blastem_libretro.so
endef

$(eval $(generic-package))
