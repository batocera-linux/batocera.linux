################################################################################
#
# ruffle
#
################################################################################

RUFFLE_VERSION = nightly-2025-02-12
RUFFLE_SITE = $(call github,ruffle-rs,ruffle,$(RUFFLE_VERSION))
RUFFLE_LICENSE = GPLv2
RUFFLE_DEPENDENCIES = host-rustc host-rust-bin openssl udev nghttp2 alsa-lib

RUFFLE_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),debug,release)
RUFFLE_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(RUFFLE_CARGO_MODE)

define RUFFLE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/$(RUFFLE_BIN_DIR)/ruffle_desktop \
             $(TARGET_DIR)/usr/bin/ruffle
endef

$(eval $(cargo-package))
