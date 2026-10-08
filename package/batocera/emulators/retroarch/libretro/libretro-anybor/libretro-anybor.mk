################################################################################
#
# libretro-anybor
#
################################################################################
# Version: 0.1.28
LIBRETRO_ANYBOR_VERSION = 2c80e3d0beb968bc4b56ec2fd8473b54eecaa306
LIBRETRO_ANYBOR_SITE = $(call github,retrodiv,AnyBOR-libretro,$(LIBRETRO_ANYBOR_VERSION))
# multiple, see https://github.com/retrodiv/AnyBOR-libretro/tree/main/LICENSES
# OpenBOR 3400 retains its no-sale terms; see LICENSES.md.
LIBRETRO_ANYBOR_LICENSE = BSD-3-Clause, OpenBOR-3400 (no sale), MIT, ISC, Zlib, Libpng-2.0, CC0-1.0, other
LIBRETRO_ANYBOR_LICENSE_FILES = LICENSE LICENSES.md NOTICE.txt
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
	    CONFIGURE_HOST="$(GNU_TARGET_NAME)" \
	    CONFIGURE_BUILD="$(GNU_HOST_NAME)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_ANYBOR_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_ANYBOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/anybor_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/anybor_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
