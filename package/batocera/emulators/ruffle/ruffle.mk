################################################################################
#
# ruffle
#
################################################################################

RUFFLE_VERSION = nightly-2024-12-28
RUFFLE_SITE = $(call github,ruffle-rs,ruffle,$(RUFFLE_VERSION))
RUFFLE_LICENSE = GPLv2
RUFFLE_DEPENDENCIES = host-rustc host-rust-bin openssl udev nghttp2 alsa-lib

RUFFLE_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),,release)
RUFFLE_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(RUFFLE_CARGO_MODE)

define RUFFLE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/$(RUFFLE_BIN_DIR)/ruffle_desktop \
             $(TARGET_DIR)/usr/bin/ruffle
endef

define RUFFLE_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ruffle/flash.ruffle.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

RUFFLE_POST_INSTALL_TARGET_HOOKS = RUFFLE_EVMAPY

$(eval $(cargo-package))
