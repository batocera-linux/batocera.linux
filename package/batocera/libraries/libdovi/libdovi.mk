################################################################################
#
# libdovi
#
################################################################################

LIBDOVI_VERSION = 2.3.3
LIBDOVI_SITE = $(call github,quietvoid,dovi_tool,$(LIBDOVI_VERSION))
LIBDOVI_LICENSE = MIT license
LIBDOVI_LICENSE_FILES = LICENSE
LIBDOVI_INSTALL_STAGING = YES
LIBDOVI_SUBDIR = dolby_vision

LIBDOVI_DEPENDENCIES = host-cargo-c

# Strip unused dev-dependencies and benchmarks, then update Cargo.lock to match
define LIBDOVI_REMOVE_DEV_DEPS
	sed -i '/\[dev-dependencies\]/,/criterion/d' $(@D)/dolby_vision/Cargo.toml
	sed -i '/\[\[bench\]\]/,/harness = false/d' $(@D)/dolby_vision/Cargo.toml
	cd $(@D)/dolby_vision && $(TARGET_MAKE_ENV) $(PKG_CARGO_ENV) cargo update --offline
endef
LIBDOVI_POST_PATCH_HOOKS += LIBDOVI_REMOVE_DEV_DEPS

define LIBDOVI_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(PKG_CARGO_ENV) \
		cargo cbuild --release --offline --locked --manifest-path \
		$(@D)/dolby_vision/Cargo.toml --target $(RUSTC_TARGET_NAME) --prefix /usr
endef

define LIBDOVI_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(PKG_CARGO_ENV) \
		cargo cinstall --release --offline --locked --manifest-path \
		$(@D)/dolby_vision/Cargo.toml --target $(RUSTC_TARGET_NAME) \
		--prefix /usr --destdir $(STAGING_DIR)
endef

define LIBDOVI_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(PKG_CARGO_ENV) \
		cargo cinstall --release --offline --locked --manifest-path \
		$(@D)/dolby_vision/Cargo.toml --target $(RUSTC_TARGET_NAME) \
		--prefix /usr --destdir $(TARGET_DIR)
endef

$(eval $(cargo-package))
