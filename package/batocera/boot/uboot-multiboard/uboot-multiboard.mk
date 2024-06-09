################################################################################
#
# uboot multiboard
#
################################################################################
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H6)$(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
UBOOT_MULTIBOARD_VERSION = 2024.01
else
UBOOT_MULTIBOARD_VERSION = 2023.01
endif

UBOOT_MULTIBOARD_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_MULTIBOARD_DL_SUBDIR = uboot
UBOOT_MULTIBOARD_SOURCE = u-boot-$(UBOOT_MULTIBOARD_VERSION).tar.bz2
UBOOT_MULTIBOARD_DEPENDENCIES = host-python3 host-python-setuptools
UBOOT_MULTIBOARD_DEPENDENCIES += host-swig host-openssl host-gnutls

ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_H3),y)
UBOOT_MULTIBOARD_DEPENDENCIES += arm-trusted-firmware
endif

# Default make opts, adaptation of buildroot uboot's opts. "-I $(HOST_DIR)/include"
# prevents mixing openssl headers from docker (currently 3.0.2) and
# buildroot host-openssl (currently 1.1.1q) which would cause build failures.
UBOOT_MULTIBOARD_MAKE_OPTS = \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCC="$(HOSTCC) -I $(HOST_DIR)/include $(subst -I/,-isystem /,$(subst -I /,-isystem /,$(HOST_CFLAGS)))" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)"

# Adjust make opts per target SoC and SoC directories which may
# contain patches and config fragments for SoC.
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL32=$(BINARIES_DIR)/bl32.elf
UBOOT_MULTIBOARD_SOC_DIR = common-rk3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H3),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL32=$(BINARIES_DIR)/bl32.elf
UBOOT_MULTIBOARD_SOC_DIR = common-h3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.elf
UBOOT_MULTIBOARD_SOC_DIR = common-rk3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H5),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.bin
UBOOT_MULTIBOARD_MAKE_OPTS += SCP=/dev/null
UBOOT_MULTIBOARD_SOC_DIR = common-h5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H6),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.bin
UBOOT_MULTIBOARD_MAKE_OPTS += SCP=/dev/null
UBOOT_MULTIBOARD_SOC_DIR = common-h6
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.bin
UBOOT_MULTIBOARD_MAKE_OPTS += SCP=/dev/null
UBOOT_MULTIBOARD_SOC_DIR = common-h616
else
# Dummy SoC dir prevents adding common level patches twice
# in case a new target SoC starts using this package and
# doesn't define UBOOT_MULTIBOARD_SOC_DIR.
UBOOT_MULTIBOARD_SOC_DIR = "__DUMMY_DIR__"
endif

# Find any common config fragments and patches in package dir.
UBOOT_MULTIBOARD_CNF_FRAGS_COMMON = $(wildcard $(UBOOT_MULTIBOARD_PKGDIR)/*.config.fragment)
UBOOT_MULTIBOARD_PATCHES_COMMON = $(wildcard $(UBOOT_MULTIBOARD_PKGDIR)/*.patch)

# Find any SoC level config fragments and patches in SoC dir (if it exists).
UBOOT_MULTIBOARD_CNF_FRAGS_SOC = $(wildcard $(UBOOT_MULTIBOARD_PKGDIR)/$(UBOOT_MULTIBOARD_SOC_DIR)/*.config.fragment)
UBOOT_MULTIBOARD_PATCHES_SOC = $(wildcard $(UBOOT_MULTIBOARD_PKGDIR)/$(UBOOT_MULTIBOARD_SOC_DIR)/*.patch)

# Use empty extract commands because we extract (and patch, configure, build
# and install) multiple times in a loop.
define UBOOT_MULTIBOARD_EXTRACT_CMDS
endef

# Helper macro to extract U-Boot.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTIBOARD_STEP_EXTRACT
	@$(call MESSAGE,"Extract U-Boot for $(1)")
	@mkdir -p $(@D)/source-$(1)
	@$(TAR) --strip-components=1 -C $(@D)/source-$(1) $(TAR_OPTIONS) $(UBOOT_MULTIBOARD_DL_DIR)/$(UBOOT_MULTIBOARD_SOURCE)
endef

# Helper macro to patch U-Boot.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTIBOARD_STEP_PATCH
	@$(call MESSAGE,"Patch U-Boot for $(1)")
	$(eval UBOOT_MULTIBOARD_PATCHES = $(strip
		$(UBOOT_MULTIBOARD_PATCHES_COMMON)
		$(UBOOT_MULTIBOARD_PATCHES_SOC)
		$(wildcard $(UBOOT_MULTIBOARD_PKGDIR)/$(1)/*.patch)))
	$(if $(UBOOT_MULTIBOARD_PATCHES),
		$(foreach patch,$(UBOOT_MULTIBOARD_PATCHES),
			$(APPLY_PATCHES) $(@D)/source-$(1) $(dir $(patch)) $(notdir $(patch))
		)
	)
endef

# Helper macro to configure U-Boot, adaptation of buildroot pkg-kconfig's
# config and config fragment handling.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTIBOARD_STEP_CONFIGURE
	@$(call MESSAGE,"Configure U-Boot for $(1)")
	$(eval UBOOT_MULTIBOARD_CNF_FRAGS = $(strip
		$(UBOOT_MULTIBOARD_CNF_FRAGS_COMMON)
		$(UBOOT_MULTIBOARD_CNF_FRAGS_SOC)
		$(wildcard $(UBOOT_MULTIBOARD_PKGDIR)/$(1)/*.config.fragment)))
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/source-$(1) \
		O=$(@D)/build-$(1) $(UBOOT_MULTIBOARD_MAKE_OPTS) $(1)_defconfig
	$(if $(UBOOT_MULTIBOARD_CNF_FRAGS),
		support/kconfig/merge_config.sh -m \
			-O $(@D)/build-$(1) $(@D)/build-$(1)/.config \
			$(UBOOT_MULTIBOARD_CNF_FRAGS)
		$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/source-$(1) \
			O=$(@D)/build-$(1) $(UBOOT_MULTIBOARD_MAKE_OPTS) olddefconfig
	)
endef

# Helper macro to build U-Boot, adaptation of buildroot uboot's build.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTIBOARD_STEP_BUILD
	@$(call MESSAGE,"Build U-Boot for $(1)")
	$(TARGET_CONFIGURE_OPTS) \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		PKG_CONFIG_SYSROOT_DIR="/" \
		PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 \
		PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 \
		PKG_CONFIG_LIBDIR="$(HOST_DIR)/lib/pkgconfig:$(HOST_DIR)/share/pkgconfig" \
		$(MAKE) -C $(@D)/source-$(1) \
			O=$(@D)/build-$(1) $(UBOOT_MULTIBOARD_MAKE_OPTS) all
endef


# Helper macro to install U-Boot.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTIBOARD_STEP_INSTALL
	@$(call MESSAGE,"Install U-Boot for $(1)")
	@mkdir -p $(BINARIES_DIR)/uboot-multiboard/$(1)
	@$(foreach bin,$(call qstrip,$(BR2_PACKAGE_UBOOT_MULTIBOARD_BINARIES)),
		cp -f $(@D)/build-$(1)/$(bin) $(BINARIES_DIR)/uboot-multiboard/$(1)/
	)
endef

# The build loop.
define UBOOT_MULTIBOARD_BUILD_CMDS
	$(foreach config,$(call qstrip,$(BR2_PACKAGE_UBOOT_MULTIBOARD_CONFIGS)),
		$(call UBOOT_MULTIBOARD_STEP_EXTRACT,$(config))
		$(call UBOOT_MULTIBOARD_STEP_PATCH,$(config))
		$(call UBOOT_MULTIBOARD_STEP_CONFIGURE,$(config))
		$(call UBOOT_MULTIBOARD_STEP_BUILD,$(config))
		$(call UBOOT_MULTIBOARD_STEP_INSTALL,$(config))
	)
endef

$(eval $(generic-package))
