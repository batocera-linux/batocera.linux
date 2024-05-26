################################################################################
#
# openbor7530 (OpenBor 4)
#
################################################################################
 
OPENBOR7530_VERSION = v7533
OPENBOR7530_SITE = $(call github,DCurrent,openbor,$(OPENBOR7530_VERSION))
OPENBOR7530_LICENSE = BSD
OPENBOR7530_LICENSE_FILE = LICENSE

OPENBOR7530_DEPENDENCIES = libvpx sdl2 libpng libogg libvorbis host-yasm sdl2_gfx
OPENBOR7530_EXTRAOPTS=""

ifeq ($(BR2_x86_64),y)
    OPENBOR7530_EXTRAOPTS=BUILD_LINUX_LE_x86_64=1
endif

ifeq ($(BR2_riscv),y)
    OPENBOR7530_EXTRAOPTS=BUILD_LINUX=1
endif

ifeq ($(BR2_arm)$(BR2_aarch64),y)
    OPENBOR7530_EXTRAOPTS=BUILD_LINUX_LE_arm=1
endif

define OPENBOR7530_PRE_CONFIGURE_VERSION
    sed -i 's/VERSION_BUILD="[^"]*"/VERSION_BUILD="$(subst v,,$(OPENBOR7530_VERSION))"/' \
	    $(@D)/engine/version.sh
endef

define OPENBOR7530_BUILD_CMDS
    cd $(@D)/engine && chmod +x $(@D)/engine/version.sh && $(@D)/engine/version.sh
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/engine -f Makefile $(OPENBOR7530_EXTRAOPTS) VERBOSE=1
endef

define OPENBOR7530_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/engine/OpenBOR $(TARGET_DIR)/usr/bin/OpenBOR7530
endef

OPENBOR7530_PRE_CONFIGURE_HOOKS += OPENBOR7530_PRE_CONFIGURE_VERSION

$(eval $(generic-package))
