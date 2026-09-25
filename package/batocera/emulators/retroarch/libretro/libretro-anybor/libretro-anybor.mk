################################################################################
#
# libretro-anybor
#
################################################################################
# Version: Commits on Sep 24, 2026
LIBRETRO_ANYBOR_VERSION = 8d47f150bc43a70abfd3f1d799ce84b538d8f831
LIBRETRO_ANYBOR_SITE = $(call github,retrodiv,AnyBOR-libretro,$(LIBRETRO_ANYBOR_VERSION))
# multiple, see https://github.com/retrodiv/AnyBOR-libretro/tree/main/LICENSES
LIBRETRO_ANYBOR_LICENSE = GPLv2+
LIBRETRO_ANYBOR_DEPENDENCIES = retroarch zlib libpng libogg libvorbis libvpx
LIBRETRO_ANYBOR_EMULATOR_INFO = anybor.libretro.core.yml

LIBRETRO_ANYBOR_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_x86_64),y)
LIBRETRO_ANYBOR_PLATFORM = linux-x86_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_ANYBOR_PLATFORM = linux-aarch64
endif

define LIBRETRO_ANYBOR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_ANYBOR_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_ANYBOR_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_ANYBOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/anybor_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/anybor_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
