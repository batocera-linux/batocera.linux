################################################################################
#
# OPENBOR6330
#
################################################################################
# Version.: 
OPENBOR6330_VERSION = v6330
OPENBOR6330_SITE = $(call github,DCurrent,openbor,$(OPENBOR6330_VERSION))
OPENBOR6330_LICENSE = BSD

OPENBOR6330_DEPENDENCIES = libvpx sdl2 libpng libogg libvorbis host-yasm sdl2_gfx

OPENBOR6330_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
	OPENBOR6330_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_x86_i686),y)
	OPENBOR6330_EXTRAOPTS=BUILD_LINUX=1
endif
ifeq ($(BR2_arm)$(BR2_aarch64),y)
	OPENBOR6330_EXTRAOPTS=BUILD_ARM=1
endif

define OPENBOR6330_BUILD_CMDS
	cd $(@D)/engine && $(@D)/engine/version.sh
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/engine -f Makefile $(OPENBOR6330_EXTRAOPTS)
endef

define OPENBOR6330_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/engine/OpenBOR $(TARGET_DIR)/usr/bin/OpenBOR6330
endef

$(eval $(generic-package))
