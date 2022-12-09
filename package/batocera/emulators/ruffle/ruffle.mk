################################################################################
#
# ruffle
#
################################################################################
# Version: Commits on Oct 09, 2022
RUFFLE_VERSION = 10c19fef5751b3fd648fb997864f953de9ce9a72
RUFFLE_SITE = $(call github,ruffle-rs,ruffle,$(RUFFLE_VERSION))
RUFFLE_LICENSE = GPLv2
RUFFLE_DEPENDENCIES = host-rustc host-rust-bin openssl

RUFFLE_ARGS_FOR_BUILD = -L $(STAGING_DIR) -Wl,-rpath,$(STAGING_DIR)

RUFFLE_CARGO_ENV = CARGO_HOME=$(HOST_DIR)/usr/share/cargo \
    RUSTFLAGS='$(addprefix -C linker=$(TARGET_CC) -C link-args=,$(RUFFLE_ARGS_FOR_BUILD))'

RUFFLE_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),,release)
RUFFLE_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(RUFFLE_CARGO_MODE)

RUFFLE_CARGO_OPTS = \
    --$(RUFFLE_CARGO_MODE) \
        --target=$(RUSTC_TARGET_NAME) \
        --manifest-path=$(@D)/Cargo.toml

define RUFFLE_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(RUFFLE_CARGO_ENV) \
            cargo build $(RUFFLE_CARGO_OPTS)
endef

define RUFFLE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/$(RUFFLE_BIN_DIR)/ruffle_desktop \
             $(TARGET_DIR)/usr/bin/ruffle
	
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ruffle/flash.ruffle.keys $(TARGET_DIR)/usr/share/evmapy
endef

#mkdir -p $(TARGET_DIR)/usr/bin
#	cp -pr $(@D)/$(RUFFLE_BIN_DIR)/ruffle_desktop $(TARGET_DIR)/usr/bin/ruffle

$(eval $(generic-package))
