################################################################################
#
# libretro-gp32emu
#
################################################################################
# Version: Commits on Jun 9, 2026
LIBRETRO_GP32EMU_VERSION = 9ca3a72fac79eb57dd16ec21f3756e243e4a579d
LIBRETRO_GP32EMU_SITE = $(call github,gameblabla,gp32emu,$(LIBRETRO_GP32EMU_VERSION))
LIBRETRO_GP32EMU_LICENSE = BSD-3-Clause, MIT
LIBRETRO_GP32EMU_LICENSE_FILES = licenses/BSD-3-Clause-MAME-derived.txt licenses/MIT-BDMEmu-frontend.txt licenses/MIT-kuba-zip.txt
LIBRETRO_GP32EMU_DEPENDENCIES += retroarch
LIBRETRO_GP32EMU_EMULATOR_INFO = gp32emu.libretro.core.yml

define LIBRETRO_GP32EMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CC)" -C $(@D)/ \
	    -f Makefile.libretro CFLAGS="$(TARGET_CFLAGS) -std=c11 -O3 -fPIC"
endef

define LIBRETRO_GP32EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gp32emu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gp32emu_libretro.so
	$(INSTALL) -D -m 0644 $(@D)/gp32emu_libretro.info \
		$(TARGET_DIR)/usr/share/libretro/info/gp32emu_libretro.info
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
