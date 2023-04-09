################################################################################
#
# LIBRETRO-FLYCASTVL
#
################################################################################
# version.: Commits on Oct 04, 2021
LIBRETRO_FLYCASTVL_VERSION = 4a913e063c95d1fae98afc64645831de0bcad57e
LIBRETRO_FLYCASTVL_SITE = $(call github,libretro,flycast,$(LIBRETRO_FLYCASTVL_VERSION))
LIBRETRO_FLYCASTVL_LICENSE = GPLv2

LIBRETRO_FLYCASTVL_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_FLYCASTVL_EXTRA_ARGS = HAVE_OPENMP=1

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_FLYCASTVL_PLATFORM = rpi4_64
LIBRETRO_FLYCASTVL_EXTRA_ARGS += FORCE_GLES=1 ARCH=arm64 LDFLAGS=-lrt

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_FLYCASTVL_PLATFORM = rpi3_64
LIBRETRO_FLYCASTVL_EXTRA_ARGS += FORCE_GLES=1 ARCH=arm64 LDFLAGS=-lrt

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_FLYCASTVL_PLATFORM = rpi2
LIBRETRO_FLYCASTVL_EXTRA_ARGS += FORCE_GLES=1 ARCH=arm LDFLAGS=-lrt
endif

define LIBRETRO_FLYCASTVL_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile \
		platform="$(LIBRETRO_FLYCASTVL_PLATFORM)" $(LIBRETRO_FLYCASTVL_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_FLYCASTVL_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_FLYCASTVL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/flycast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/flycastvl_libretro.so

    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/retroarch/libretro/libretro-flycastvl/flycastvl_libretro.info" \
        "$(TARGET_DIR)/usr/share/libretro/info/"
endef

$(eval $(generic-package))
