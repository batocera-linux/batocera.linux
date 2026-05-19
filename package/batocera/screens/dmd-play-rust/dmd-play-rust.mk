################################################################################
#
# DMD_PLAY_RUST
#
################################################################################
DMD_PLAY_RUST_VERSION = 303d59002689d8fc4c5a4d58d4f3e832886f2531
DMD_PLAY_RUST_SITE =  $(call github,batocera-linux,dmd-play-rust,$(DMD_PLAY_RUST_VERSION))

define DMD_PLAY_RUST_DMD_PLAY_SYMLINK
	ln -sf dmd-play-rust $(TARGET_DIR)/usr/bin/dmd-play
endef

ifeq ($(BR2_PACKAGE_DMD_PLAY_RUST_DMD_PLAY_BIN),y)
DMD_PLAY_RUST_POST_INSTALL_TARGET_HOOKS += DMD_PLAY_RUST_DMD_PLAY_SYMLINK
endif

$(eval $(cargo-package))
