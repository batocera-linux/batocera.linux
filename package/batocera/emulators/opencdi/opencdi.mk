################################################################################
#
# opencdi
#
################################################################################

OPENCDI_VERSION = v0.4.2
OPENCDI_SITE = $(call github,sigsantilio,opencdi,$(OPENCDI_VERSION))
OPENCDI_LICENSE = MIT
OPENCDI_LICENSE_FILES = LICENSE
OPENCDI_DEPENDENCIES = host-rustc host-pkgconf alsa-lib udev libxkbcommon
OPENCDI_EMULATOR_INFO = opencdi.emulator.yml

OPENCDI_CARGO_BUILD_OPTS = --bin opencdi

OPENCDI_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),debug,release)
OPENCDI_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(OPENCDI_CARGO_MODE)

define OPENCDI_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/$(OPENCDI_BIN_DIR)/opencdi \
		$(TARGET_DIR)/usr/bin/opencdi
endef

$(eval $(cargo-package))
$(eval $(emulator-info-package))
