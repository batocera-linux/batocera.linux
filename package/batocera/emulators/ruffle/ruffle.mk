################################################################################
#
# ruffle
#
################################################################################

RUFFLE_VERSION = nightly-2024-03-28
RUFFLE_SITE = $(call github,ruffle-rs,ruffle,$(RUFFLE_VERSION))
RUFFLE_LICENSE = GPLv2
RUFFLE_DEPENDENCIES = host-rustc host-rust-bin openssl udev nghttp2 alsa-lib

RUFFLE_CARGO_ENV = CARGO_HOME=$(DL_DIR)/br-cargo-home \
    CARGO_BUILD_TARGET="$(RUSTC_TARGET_NAME)" \
    CARGO_HOST_RUSTFLAGS="$(addprefix -C link-args=,$(HOST_LDFLAGS))" \
    CARGO_TARGET_$(call UPPERCASE,$(RUSTC_TARGET_NAME))_LINKER=$(notdir $(TARGET_CROSS))gcc \
    PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)"

RUFFLE_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),,release)
RUFFLE_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(RUFFLE_CARGO_MODE)

RUFFLE_CARGO_OPTS = \
    --$(RUFFLE_CARGO_MODE) \
    --manifest-path=$(@D)/Cargo.toml

define RUFFLE_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) $(RUFFLE_CARGO_ENV) \
            cargo build $(RUFFLE_CARGO_OPTS)
endef

define RUFFLE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/$(RUFFLE_BIN_DIR)/ruffle_desktop \
             $(TARGET_DIR)/usr/bin/ruffle

	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ruffle/flash.ruffle.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
