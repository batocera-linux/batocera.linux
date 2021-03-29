################################################################################
#
# OPENBOR6510
#
################################################################################
# Version.: 
OPENBOR6510_VERSION = v6510-dev
OPENBOR6510_SITE = $(call github,DCurrent,openbor,$(OPENBOR6510_VERSION))
OPENBOR6510_LICENSE = BSD

OPENBOR6510_DEPENDENCIES = libvpx sdl2 libpng libogg libvorbis host-yasm sdl2_gfx

OPENBOR6510_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
	OPENBOR6510_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_x86_i686),y)
	OPENBOR6510_EXTRAOPTS=BUILD_LINUX=1
endif
ifeq ($(BR2_arm)$(BR2_aarch64),y)
	OPENBOR6510_EXTRAOPTS=BUILD_ARM=1
endif

define OPENBOR6510_BUILD_CMDS
	cd $(@D)/engine && $(@D)/engine/version.sh
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/engine -f Makefile $(OPENBOR6510_EXTRAOPTS)
endef

define OPENBOR6510_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/engine/OpenBOR $(TARGET_DIR)/usr/bin/OpenBOR6510
endef

$(eval $(generic-package))
