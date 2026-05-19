################################################################################
#
# DMD_PLAY_RUST
#
################################################################################
DMD_PLAY_RUST_VERSION = 5ddf871074dc245561ee2c5d355c60a5afeae068
DMD_PLAY_RUST_SITE =  $(call github,batocera-linux,dmd-play-rust,$(DMD_PLAY_RUST_VERSION))

define DMD_PLAY_RUST_DMD_PLAY_SYMLINK
	ln -sf dmd-play-rust $(TARGET_DIR)/usr/bin/dmd-play
endef

ifeq ($(BR2_PACKAGE_DMD_PLAY_RUST_DMD_PLAY_BIN),y)
DMD_PLAY_RUST_POST_INSTALL_TARGET_HOOKS += DMD_PLAY_RUST_DMD_PLAY_SYMLINK
endif

$(eval $(cargo-package))
