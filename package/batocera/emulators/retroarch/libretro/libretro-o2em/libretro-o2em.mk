################################################################################
#
# O2EM
#
################################################################################
# Version.: Commits on Aug 5, 2021
LIBRETRO_O2EM_VERSION = e09a952964dea7ef164a634288e1134dba6e4a56
LIBRETRO_O2EM_SITE = $(call github,libretro,libretro-o2em,$(LIBRETRO_O2EM_VERSION))
LIBRETRO_O2EM_LICENSE = Artistic License

LIBRETRO_O2EM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_O2EM_PLATFORM = armv neon

else ifeq ($(BR2_aarch64),y)
LIBRETRO_O2EM_PLATFORM = unix
endif

define LIBRETRO_O2EM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_O2EM_PLATFORM)"
endef

define LIBRETRO_O2EM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/o2em_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/o2em_libretro.so
endef

$(eval $(generic-package))
