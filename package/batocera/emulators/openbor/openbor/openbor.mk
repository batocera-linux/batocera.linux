################################################################################
#
# OPENBOR
#
################################################################################
# Version.: 
OPENBOR_VERSION = 7a45a2215a0cc12c1085d92e7b210a827ea552c2
OPENBOR_SITE = $(call github,DCurrent,openbor,$(OPENBOR_VERSION))
OPENBOR_LICENSE = BSD

OPENBOR_DEPENDENCIES = libvpx sdl2 libpng libogg libvorbis host-yasm

OPENBOR_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
	OPENBOR_EXTRAOPTS=BUILD_LINUX=1 BUILD_PLATFORM=x86_64
endif
ifeq ($(BR2_x86_i686),y)
	OPENBOR_EXTRAOPTS=BUILD_LINUX=1
endif
ifeq ($(BR2_arm)$(BR2_aarch64),y)
	OPENBOR_EXTRAOPTS=BUILD_ARM=1
endif

define OPENBOR_BUILD_CMDS
	cd $(@D)/engine && $(@D)/engine/version.sh
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/engine -f Makefile $(OPENBOR_EXTRAOPTS)
endef

define OPENBOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/engine/OpenBOR $(TARGET_DIR)/usr/bin/OpenBOR
endef

$(eval $(generic-package))
