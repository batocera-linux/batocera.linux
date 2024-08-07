################################################################################
#
# libretro-minivmac
#
################################################################################
# Version: Commits on Jul 1, 2024
LIBRETRO_MINIVMAC_VERSION = 7de54a87e2527eb15b9ec2ac589e041c3d051d49
LIBRETRO_MINIVMAC_SITE = https://github.com/libretro/libretro-minivmac
LIBRETRO_MINIVMAC_LICENSE = GPLv2
LIBRETRO_MINIVMAC_SITE_METHOD=git
LIBRETRO_MINIVMAC_GIT_SUBMODULES=YES

LIBRETRO_MINIVMAC_DEPENDENCIES = 

define LIBRETRO_MINIVMAC_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
        -C $(@D)/ -f Makefile platform=unix \
        GIT_VERSION="-$(shell echo $(LIBRETRO_MINIVMAC_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_MINIVMAC_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/minivmac_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/minivmac_libretro.so
endef

$(eval $(generic-package))
