################################################################################
#
# evsieve
#
################################################################################

EVSIEVE_VERSION = bd9d6e43fc0572c68f4645e07b0aff45dbe05b58
EVSIEVE_SOURCE = foo-$(EVSIEVE_VERSION).tar.gz
EVSIEVE_SITE = $(call github,KarsMulder,evsieve,$(EVSIEVE_VERSION))
EVSIEVE_LICENSE = GPLv2
EVSIEVE_LICENSE_FILES = COPYING

EVSIEVE_DEPENDENCIES = host-rustc libevdev

EVSIEVE_ARGS_FOR_BUILD = -L $(STAGING_DIR) -Wl,-rpath,$(STAGING_DIR)
EVSIEVE_CARGO_ENV = CARGO_HOME=$(HOST_DIR)/share/cargo RUSTFLAGS='$(addprefix -C linker=$(TARGET_CC) -C link-args=,$(EVSIEVE_ARGS_FOR_BUILD))'

EVSIEVE_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(EVSIEVE_CARGO_MODE)

EVSIEVE_CARGO_OPTS = \
 	$(if $(BR2_ENABLE_DEBUG),,--release) \
 	--target=$(RUSTC_TARGET_NAME) \
 	--manifest-path=$(@D)/Cargo.toml

define EVSIEVE_BUILD_CMDS
 	$(TARGET_MAKE_ENV) $(EVSIEVE_CARGO_ENV) \
 		cargo build $(EVSIEVE_CARGO_OPTS)
endef

define EVSIEVE_INSTALL_TARGET_CMDS
 	$(INSTALL) -D -m 0755 $(@D)/$(EVSIEVE_BIN_DIR)release/evsieve \
 		$(TARGET_DIR)/usr/bin/evsieve
 	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/evsieve/evsieve-merge-devices \
 		$(TARGET_DIR)/usr/bin/evsieve-merge-devices
	$(TARGET_STRIP) -s $(TARGET_DIR)/usr/bin/evsieve
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/evsieve/evsieve-helper $(TARGET_DIR)/usr/bin/evsieve-helper
endef

$(eval $(generic-package))
