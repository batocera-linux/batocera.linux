################################################################################
#
# libretro-mesens
#
################################################################################
# Version: Commits on Jul 25, 2022
LIBRETRO_MESENS_VERSION = 32a7adfb4edb029324253cb3632dfc6599ad1aa8
LIBRETRO_MESENS_SITE = $(call github,libretro,Mesen-S,$(LIBRETRO_MESENS_VERSION))
LIBRETRO_MESENS_LICENSE = GPL

define LIBRETRO_MESENS_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION="" -C $(@D)/Libretro -f Makefile
endef

define LIBRETRO_MESENS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen-s_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen-s_libretro.so
endef

$(eval $(generic-package))
