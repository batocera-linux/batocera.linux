################################################################################
#
# RUFFLE
#
################################################################################
# Version.: Commits on Mar 27, 2021
RUFFLE_VERSION = 5cefaa16d2c29dac0e573967477126f31bb69075
RUFFLE_SITE = $(call github,ruffle-rs,ruffle,$(RUFFLE_VERSION))
RUFFLE_LICENSE = GPLv2
RUFFLE_DEPENDENCIES = host-rustc openssl

RUFFLE_CARGO_ENV = \
    CARGO_HOME=$(HOST_DIR)/usr/share/cargo \
    RUST_TARGET_PATH=$(HOST_DIR)/etc/rustc \
    PKG_CONFIG_SYSROOT_DIR=$(STAGING_DIR) \
    PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig \
    TARGET_CC=$(TARGET_CC) \
    TARGET_CXX=$(TARGET_CXX) \
    TARGET_LD=$(TARGET_LD)

RUFFLE_CARGO_OPTS = \
    --target=$(BR2_ARCH)-unknown-linux-gnu \
    --manifest-path=$(@D)/Cargo.toml

RUFFLE_CARGO_MODE = release
RUFFLE_CARGO_OPTS += --$(RUFFLE_CARGO_MODE)

define RUFFLE_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(RUFFLE_CARGO_ENV) \
            cargo build $(RUFFLE_CARGO_OPTS)
endef

define RUFFLE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	cp -pr $(@D)/target/x86_64-unknown-linux-gnu/release/ruffle_desktop $(TARGET_DIR)/usr/bin/ruffle

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ruffle/flash.ruffle.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
