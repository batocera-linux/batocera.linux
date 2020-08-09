################################################################################
#
# BLASTEM
#
################################################################################
# Version.: Commits on Jul 19, 2020
LIBRETRO_BLASTEM_VERSION = 4c418ee9a9d8
LIBRETRO_BLASTEM_SOURCE = $(LIBRETRO_BLASTEM_VERSION).tar.gz
LIBRETRO_BLASTEM_SITE = https://www.retrodev.com/repos/blastem/archive

LIBRETRO_BLASTEM_LICENSE = Non-commercial

LIBRETRO_BLASTEM_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
        LIBRETRO_BLASTEM_EXTRAOPTS=CPU=x86_64
endif
ifeq ($(BR2_x86_i586),y)
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

