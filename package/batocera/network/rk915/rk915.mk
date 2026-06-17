################################################################################
#
# rk915 — Rockchip RK915 SDIO WiFi driver (ported from BSP 4.4 to mainline)
#
################################################################################

# Local source — tarball must be placed in Batocera's dl/ directory
# Create it with: tar czf rk915-1.0.tar.gz --transform='s,^,rk915-1.0/,' \
#                   -C /path/to/rk915-ported Makefile Kconfig inc/ shared/ src/
RK915_VERSION = bf237144d8fde7dffaef1777350b23d5d40d0920
RK915_SITE = $(call github,ImanolBarba,rk915,$(RK915_VERSION))
RK915_LICENSE = GPL-2.0
RK915_LICENSE_FILES = LICENSE

RK915_MODULE_MAKE_OPTS = \
	CONFIG_RK915=m \
	USER_EXTRA_CFLAGS="-Wno-error"

# Install firmware files to /lib/firmware/
# These must be extracted from the stock R36 Ultra ROM and placed alongside
# the package source, or bundled inside the tarball under firmware/
define RK915_INSTALL_FIRMWARE
	mkdir -p $(TARGET_DIR)/lib/firmware
	if [ -d $(@D)/firmware ]; then \
		cp -f $(@D)/firmware/rk915_fw.bin $(TARGET_DIR)/lib/firmware/ 2>/dev/null || true; \
		cp -f $(@D)/firmware/rk915_patch.bin $(TARGET_DIR)/lib/firmware/ 2>/dev/null || true; \
	fi
endef

RK915_POST_INSTALL_TARGET_HOOKS = RK915_INSTALL_FIRMWARE

$(eval $(kernel-module))
$(eval $(generic-package))
