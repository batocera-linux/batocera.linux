################################################################################
#
# libretro-vitaquake3
#
################################################################################
# Version: Commits on Jan 31, 2021
LIBRETRO_VITAQUAKE3_VERSION = 7a633867cf0a35c71701aef6fc9dd9dfab9c33a9
LIBRETRO_VITAQUAKE3_SITE = $(call github,libretro,vitaquake3,$(LIBRETRO_VITAQUAKE3_VERSION))
LIBRETRO_VITAQUAKE3_LICENSE = GPL-2.0
LIBRETRO_VITAQUAKE3_LICENSE_FILE = COPYING.txt

LIBRETRO_VITAQUAKE3_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_VITAQUAKE3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile platform="$(LIBRETRO_VITAQUAKE3_PLATFORM)"
endef

define LIBRETRO_VITAQUAKE3_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vitaquake3_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/
endef

$(eval $(generic-package))
