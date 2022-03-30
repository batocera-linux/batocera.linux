################################################################################
#
# libretro-dosbox-pure
#
################################################################################
# Version: Commits on Mar 21, 2022
LIBRETRO_DOSBOX_PURE_VERSION = 7ba6aea1797e10c0d3900a6b21a0b874e33b7df2
LIBRETRO_DOSBOX_PURE_SITE = $(call github,schellingb,dosbox-pure,$(LIBRETRO_DOSBOX_PURE_VERSION))
LIBRETRO_DOSBOX_PURE_LICENSE = GPLv2

LIBRETRO_DOSBOX_PURE_PLATFORM=$(BATOCERA_SYSTEM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_DOSBOX_PURE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_DOSBOX_PURE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_DOSBOX_PURE_PLATFORM = rpi3
    else
        LIBRETRO_DOSBOX_PURE_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_DOSBOX_PURE_PLATFORM = rpi4
endif

# x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=x86 WITH_FAKE_SDL=1

# x86_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=x86_64 WITH_FAKE_SDL=1

else ifeq ($(BR2_arm),y)
LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=arm WITH_FAKE_SDL=1

else ifeq ($(BR2_aarch64),y)
LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=arm64 WITH_FAKE_SDL=1
endif

define LIBRETRO_DOSBOX_PURE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" cross_prefix="$(STAGING_DIR)/usr/bin/" -C $(@D) -f Makefile \
		platform=$(LIBRETRO_DOSBOX_PURE_PLATFORM) $(LIBRETRO_DOSBOX_PURE_EXTRA_ARGS)
endef

define LIBRETRO_DOSBOX_PURE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dosbox_pure_libretro.so \
	  $(TARGET_DIR)/usr/lib/libretro/dosbox_pure_libretro.so
endef

$(eval $(generic-package))
