################################################################################
#
# DOSBOX PURE
#
################################################################################
# Version.: Commits on Dec 21, 2020
LIBRETRO_DOSBOX_PURE_VERSION = 1502730ed7078e0f91e3dc82608dd5d7755c63b3
LIBRETRO_DOSBOX_PURE_SITE = https://github.com/schellingb/dosbox-pure.git
LIBRETRO_DOSBOX_PURE_SITE_METHOD=git
LIBRETRO_DOSBOX_PURE_GIT_SUBMODULES=YES
LIBRETRO_DOSBOX_PURE_LICENSE = GPLv2

# x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=x86 WITH_FAKE_SDL=1
endif

# x86_64
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=x86_64 WITH_FAKE_SDL=1
endif

ifeq ($(BR2_arm),y)
	LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=arm WITH_FAKE_SDL=1
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_DOSBOX_PURE_EXTRA_ARGS = target=arm64 WITH_FAKE_SDL=1
endif

define LIBRETRO_DOSBOX_PURE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" cross_prefix="$(STAGING_DIR)/usr/bin/" -C $(@D) -f Makefile \
		platform=$(BATOCERA_SYSTEM) $(LIBRETRO_DOSBOX_PURE_EXTRA_ARGS)
endef

define LIBRETRO_DOSBOX_PURE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dosbox_pure_libretro.so \
	  $(TARGET_DIR)/usr/lib/libretro/dosbox_pure_libretro.so
endef

$(eval $(generic-package))
