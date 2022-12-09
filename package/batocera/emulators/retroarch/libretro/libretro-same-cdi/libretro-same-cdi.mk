################################################################################
#
# libretro-same-cdi
#
################################################################################
# Version: Commits on Feb 15. 2022
LIBRETRO_SAME_CDI_VERSION = dcc76a5
LIBRETRO_SAME_CDI_SITE = $(call github,libretro,same_cdi,$(LIBRETRO_SAME_CDI_VERSION))
LIBRETRO_SAME_CDI_LICENSE = GPL

define LIBRETRO_SAME_CDI_BUILD_CMDS
	$(HOST_CONFIGURE_OPTS) $(MAKE) -C $(@D)/3rdparty/genie/build/gmake.linux -f genie.make
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION="" -C $(@D) -f Makefile.libretro
endef

define LIBRETRO_SAME_CDI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/same_cdi_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/same_cdi_libretro.so
endef

$(eval $(generic-package))
