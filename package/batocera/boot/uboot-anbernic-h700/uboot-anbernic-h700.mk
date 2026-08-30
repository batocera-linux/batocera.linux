################################################################################
#
# uboot-anbernic-h700
#
################################################################################

UBOOT_ANBERNIC_H700_VERSION = 2026.04
UBOOT_ANBERNIC_H700_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_ANBERNIC_H700_SOURCE = u-boot-$(UBOOT_ANBERNIC_H700_VERSION).tar.bz2
UBOOT_ANBERNIC_H700_LICENSE = GPL-2.0+
UBOOT_ANBERNIC_H700_LICENSE_FILES = Licenses/README
UBOOT_ANBERNIC_H700_INSTALL_IMAGES = YES

# Arm Trusted Firmware
UBOOT_ANBERNIC_H700_TFA_VERSION = lts-v2.14.3
UBOOT_ANBERNIC_H700_EXTRA_DOWNLOADS = \
    https://github.com/ARM-software/arm-trusted-firmware/archive/refs/tags/$(UBOOT_ANBERNIC_H700_TFA_VERSION).tar.gz

UBOOT_ANBERNIC_H700_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex \
    host-python-setuptools host-dtc host-swig host-gnutls host-python-pyelftools

# Extract Arm Trusted Firmware
define UBOOT_ANBERNIC_H700_EXTRACT_TFA
	mkdir -p $(@D)/tf-a
	$(TAR) -xf $(UBOOT_ANBERNIC_H700_DL_DIR)/$(UBOOT_ANBERNIC_H700_TFA_VERSION).tar.gz \
		-C $(@D)/tf-a --strip-components=1
endef

define UBOOT_ANBERNIC_H700_COPY_DEFCONFIGS
	cp -f $(UBOOT_ANBERNIC_H700_PKGDIR)/anbernic_rg35xx_h700_lpddr3_defconfig \
	    $(@D)/configs/anbernic_rg35xx_h700_lpddr3_defconfig
	cp -f $(UBOOT_ANBERNIC_H700_PKGDIR)/anbernic_rg35xx_h700_lpddr4_defconfig \
	    $(@D)/configs/anbernic_rg35xx_h700_lpddr4_defconfig
endef

UBOOT_ANBERNIC_H700_POST_EXTRACT_HOOKS += UBOOT_ANBERNIC_H700_EXTRACT_TFA
UBOOT_ANBERNIC_H700_POST_EXTRACT_HOOKS += UBOOT_ANBERNIC_H700_COPY_DEFCONFIGS

# H700 belongs to the sun50i_h616 family
UBOOT_ANBERNIC_H700_TFA_PLAT = sun50i_h616
UBOOT_ANBERNIC_H700_BL31 = $(@D)/tf-a/build/$(UBOOT_ANBERNIC_H700_TFA_PLAT)/release/bl31.bin

UBOOT_ANBERNIC_H700_MAKE_OPTS = \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCFLAGS="$(HOST_CFLAGS)" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)" \
	BL31=$(UBOOT_ANBERNIC_H700_BL31) \
	SCP=/dev/null

UBOOT_BOARDS = \
	anbernic_rg35xx_h700:anbernic_rg35xx_h700_lpddr4_defconfig \
	anbernic_rg35xx_h700_lpddr3:anbernic_rg35xx_h700_lpddr3_defconfig

define UBOOT_ANBERNIC_H700_BUILD_CMDS
	# Build TF-A (BL31) once
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/tf-a \
		CROSS_COMPILE="$(TARGET_CROSS)" \
		PLAT=$(UBOOT_ANBERNIC_H700_TFA_PLAT) \
		bl31

	# Build each U-Boot variant
	for pair in $(UBOOT_BOARDS); do \
		board=$${pair%%:*}; \
		defconfig=$${pair##*:}; \
		echo "---- Building Mainline U-Boot for $${board} ($${defconfig}) ----"; \
		$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ANBERNIC_H700_MAKE_OPTS) mrproper && \
		$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ANBERNIC_H700_MAKE_OPTS) $${defconfig} && \
		$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ANBERNIC_H700_MAKE_OPTS) && \
		mkdir -p $(@D)/staging/$${board} && \
		cp -v $(@D)/u-boot-sunxi-with-spl.bin $(@D)/staging/$${board}/ || exit 1; \
	done

	# Compile DT overlay for DDR3 boards
	$(HOST_DIR)/bin/dtc -@ -I dts -O dtb \
		-o $(@D)/sun50i-h700-anbernic-rg35xx-2024-ddr3.dtbo \
		$(UBOOT_ANBERNIC_H700_PKGDIR)/sun50i-h700-anbernic-rg35xx-2024-ddr3.dts
endef

define UBOOT_ANBERNIC_H700_INSTALL_IMAGES_CMDS
	for pair in $(UBOOT_BOARDS); do \
		board=$${pair%%:*}; \
		mkdir -p $(BINARIES_DIR)/$${board}; \
		cp -v $(@D)/staging/$${board}/u-boot-sunxi-with-spl.bin \
			$(BINARIES_DIR)/$${board}/u-boot-sunxi-with-spl.bin; \
	done
	cp -v $(@D)/sun50i-h700-anbernic-rg35xx-2024-ddr3.dtbo $(BINARIES_DIR)/
endef

$(eval $(generic-package))
