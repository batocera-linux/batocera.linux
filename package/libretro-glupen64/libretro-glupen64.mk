################################################################################
#
# GLUPEN64
#
################################################################################
LIBRETRO_GLUPEN64_VERSION = 211792edaabaee76a51b69d4cf077a17e422f816
LIBRETRO_GLUPEN64_SITE = $(call github,loganmc10,GLupeN64,$(LIBRETRO_GLUPEN64_VERSION))
LIBRETRO_GLUPEN64_GIT = https://github.com/loganmc10/GLupeN64.git
LIBRETRO_GLUPEN64_DEPENDENCIES = rpi-userland

# Reused the dirty hack form PPSPP package to download submodules
define LIBRETRO_GLUPEN64_EXTRACT_CMDS
	rm -rf $(@D)
	git clone --recursive --depth 1 $(LIBRETRO_GLUPEN64_GIT) $(@D)
	touch $(@D)/.stamp_downloaded
endef

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
	LIBRETRO_GLUPEN64_PLATFORM=rpi3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
	LIBRETRO_GLUPEN64_PLATFORM=rpi2
endif

define LIBRETRO_GLUPEN64_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_GLUPEN64_PLATFORM)"
endef

define LIBRETRO_GLUPEN64_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/glupen64_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/glupen64_libretro.so
endef

define GLUPEN64_CROSS_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/Makefile
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/Makefile
endef

GLUPEN64_PRE_CONFIGURE_HOOKS += GLUPEN64_FIXUP

$(eval $(generic-package))
