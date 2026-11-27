################################################################################
#
# libretro-anybor
#
################################################################################
# Version: 0.3.0
LIBRETRO_ANYBOR_VERSION = 4e93b1e9f41af3c433e5f3db72b5d679bf6e8cac
LIBRETRO_ANYBOR_SITE = $(call github,retrodiv,AnyBOR-libretro,$(LIBRETRO_ANYBOR_VERSION))
# multiple, see https://github.com/retrodiv/AnyBOR-libretro/tree/main/LICENSES
# OpenBOR 3400 and 3741 retain their no-sale terms; see LICENSES.md.
LIBRETRO_ANYBOR_LICENSE = BSD-3-Clause, OpenBOR-3400 (no sale), OpenBOR-3741 (no sale), MIT, ISC, Zlib, Libpng-2.0, CC0-1.0, other
LIBRETRO_ANYBOR_LICENSE_FILES = LICENSE LICENSES.md NOTICE.txt
LIBRETRO_ANYBOR_DEPENDENCIES = host-pkgconf retroarch zlib libpng libogg libvorbis libvpx libarchive
LIBRETRO_ANYBOR_EMULATOR_INFO = anybor.libretro.core.yml

# AnyBOR wraps codec allocations inside each engine's relocatable link.
ifeq ($(BR2_PACKAGE_LIBRETRO_ANYBOR),y)
LIBOGG_CONF_OPTS += -DOGG_BUILD_STATIC_LIBS=ON
LIBVORBIS_CONF_OPTS += --with-pic
endif

LIBRETRO_ANYBOR_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_x86_64),y)
LIBRETRO_ANYBOR_PLATFORM = linux-x86_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_ANYBOR_PLATFORM = linux-aarch64
else ifeq ($(BR2_RISCV_64),y)
LIBRETRO_ANYBOR_PLATFORM = linux-riscv64
endif

# fopen64 from LFS defines escapes the core's file wrappers
define LIBRETRO_ANYBOR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
	    CFLAGS="$(filter-out -D_FILE_OFFSET_BITS=64,$(TARGET_CFLAGS))" \
	    CXXFLAGS="$(filter-out -D_FILE_OFFSET_BITS=64,$(TARGET_CXXFLAGS))" \
	    $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_ANYBOR_PLATFORM)" \
	    SYSTEM_DEPS=1
endef

define LIBRETRO_ANYBOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/anybor_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/anybor_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
