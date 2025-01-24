################################################################################
#
# libretro-holani
#
################################################################################

LIBRETRO_HOLANI_VERSION = 0.9.6-1
LIBRETRO_HOLANI_SITE = $(call github,lleny,holani-retro,$(LIBRETRO_HOLANI_VERSION))
LIBRETRO_HOLANI_LICENSE = GPLv3
LIBRETRO_HOLANI_DEPENDENCIES = host-rustc host-rust-bin host-clang retroarch

LIBRETRO_HOLANI_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),,release)
LIBRETRO_HOLANI_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(LIBRETRO_HOLANI_CARGO_MODE)

define LIBRETRO_HOLANI_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/$(LIBRETRO_HOLANI_BIN_DIR)/libholani.so \
             $(TARGET_DIR)/usr/lib/libretro/holani_libretro.so
    $(INSTALL) -D $(@D)/res/holani_libretro.info \
    	     $(TARGET_DIR)/usr/share/libretro/info/holani_libretro.info
endef

$(eval $(cargo-package))
