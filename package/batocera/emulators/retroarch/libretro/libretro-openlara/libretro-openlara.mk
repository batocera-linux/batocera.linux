################################################################################
#
# libretro-openlara
#
################################################################################
# Version: Commits on Nov 16, 2022
LIBRETRO_OPENLARA_VERSION = 96989ac41ae55a42b19916dc8191f74be40e1b07
LIBRETRO_OPENLARA_SITE = $(call github,libretro,openlara,$(LIBRETRO_OPENLARA_VERSION))
LIBRETRO_OPENLARA_LICENSE = BSD 2-Clause
LIBRETRO_OPENLARA_LICENSE_FILES = LICENSE

LIBRETRO_OPENLARA_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_OPENLARA_EXTRA_ARGS = CORE=1

# x86 should use opengl for retroarch
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
    ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
        LIBRETRO_OPENLARA_EXTRA_ARGS += GLES=1 GLES31=1
	else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
	    LIBRETRO_OPENLARA_EXTRA_ARGS += GLES=1
	endif
endif

define LIBRETRO_OPENLARA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/src/platform/libretro -f Makefile $(LIBRETRO_OPENLARA_EXTRA_ARGS) \
		platform="$(LIBRETRO_OPENLARA_PLATFORM)"
endef

define LIBRETRO_OPENLARA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/platform/libretro/openlara_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/openlara_libretro.so
endef

$(eval $(generic-package))
