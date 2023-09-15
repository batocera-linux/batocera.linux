################################################################################
#
# OPENBOR6412
#
################################################################################
# Version.: 
OPENBOR6412_VERSION = 05af203b0e5676034678291bbedc0b9fe4c8f898
OPENBOR6412_SITE = $(call github,DCurrent,openbor,$(OPENBOR6412_VERSION))
OPENBOR6412_LICENSE = BSD

OPENBOR6412_DEPENDENCIES = libvpx sdl2 libpng libogg libvorbis host-yasm sdl2_gfx

OPENBOR6412_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
	OPENBOR6412_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_riscv),y)
	OPENBOR6412_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_x86_i686),y)
	OPENBOR6412_EXTRAOPTS=BUILD_LINUX=1
endif
ifeq ($(BR2_arm)$(BR2_aarch64),y)
	OPENBOR6412_EXTRAOPTS=BUILD_ARM=1
endif

define OPENBOR6412_BUILD_CMDS
	cd $(@D)/engine && $(@D)/engine/version.sh
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/engine -f Makefile $(OPENBOR6412_EXTRAOPTS)
endef

define OPENBOR6412_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/engine/OpenBOR $(TARGET_DIR)/usr/bin/OpenBOR6412
endef

$(eval $(generic-package))
