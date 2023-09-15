################################################################################
#
# OPENBOR7142
#
################################################################################
# Version.: 
OPENBOR7142_VERSION = 3caaddd5545ea916aaeef329ba43c9f2c4a451cc
OPENBOR7142_SITE = $(call github,DCurrent,openbor,$(OPENBOR7142_VERSION))
OPENBOR7142_LICENSE = BSD

OPENBOR7142_DEPENDENCIES = libvpx sdl2 libpng libogg libvorbis host-yasm sdl2_gfx
OPENBOR7142_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
	OPENBOR7142_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_riscv),y)
	OPENBOR7142_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_x86_i686),y)
	OPENBOR7142_EXTRAOPTS=BUILD_LINUX=1
endif
ifeq ($(BR2_arm)$(BR2_aarch64),y)
	OPENBOR7142_EXTRAOPTS=BUILD_ARM=1
endif

define OPENBOR7142_BUILD_CMDS
	cd $(@D)/engine && $(@D)/engine/version.sh
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/engine -f Makefile $(OPENBOR7142_EXTRAOPTS)
endef

define OPENBOR7142_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/engine/OpenBOR $(TARGET_DIR)/usr/bin/OpenBOR7142
endef

$(eval $(generic-package))
