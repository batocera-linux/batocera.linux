################################################################################
#
# libretro-holani
#
################################################################################

LIBRETRO_HOLANI_VERSION = 1.0.0
LIBRETRO_HOLANI_SITE = $(call github,lleny,holani-retro,$(LIBRETRO_HOLANI_VERSION))
LIBRETRO_HOLANI_LICENSE = GPLv3
LIBRETRO_HOLANI_DEPENDENCIES = host-rustc host-rust-bin host-clang retroarch
LIBRETRO_HOLANI_EMULATOR_INFO = holani.libretro.core.yml

LIBRETRO_HOLANI_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),debug,release)
LIBRETRO_HOLANI_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(LIBRETRO_HOLANI_CARGO_MODE)

define LIBRETRO_HOLANI_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/$(LIBRETRO_HOLANI_BIN_DIR)/libholani.so \
             $(TARGET_DIR)/usr/lib/libretro/holani_libretro.so
    $(INSTALL) -D $(@D)/res/holani_libretro.info \
    	     $(TARGET_DIR)/usr/share/libretro/info/holani_libretro.info
endef

# 001-fix-build-with-clang-22.patch modifies a vendored file, so cargo's
# checksum for it has to be updated too. This is done with sed instead of in
# the patch because the layout of .cargo-checksum.json changes between cargo
# versions (1.97 added a "$comment" key).
define LIBRETRO_HOLANI_FIX_VENDOR_CHECKSUM
	sed -i 's/db5f695c60359f8a9cf3bd57dde0bd2f37f91f2ac66cb4b0d76932961bdb1351/220bd363eaab7d9422914a5845bfcb405d895443df09f12ccf3f49b86b87ea20/' \
		$(@D)/VENDOR/libretro-rs-ffi/.cargo-checksum.json
endef
LIBRETRO_HOLANI_POST_PATCH_HOOKS += LIBRETRO_HOLANI_FIX_VENDOR_CHECKSUM

$(eval $(cargo-package))
$(eval $(emulator-info-package))