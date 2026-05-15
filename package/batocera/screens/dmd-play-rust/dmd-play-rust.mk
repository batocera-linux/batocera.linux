################################################################################
#
# DMD_PLAY_RUST
#
################################################################################
DMD_PLAY_RUST_VERSION = 55c0f931aa89a4545902991e81904f3e7a3b5455
DMD_PLAY_RUST_SITE =  $(call github,batocera-linux,dmd-play-rust,$(DMD_PLAY_RUST_VERSION))

define DMD_PLAY_RUST_DMD_PLAY_SYMLINK
	ln -sf dmd-play-rust $(TARGET_DIR)/usr/bin/dmd-play
endef

ifeq ($(BR2_PACKAGE_DMD_PLAY_RUST_DMD_PLAY_BIN),y)
DMD_PLAY_RUST_POST_INSTALL_TARGET_HOOKS += DMD_PLAY_RUST_DMD_PLAY_SYMLINK
endif

$(eval $(cargo-package))
