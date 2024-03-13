################################################################################
#
# uboot multi H616/H618
#
################################################################################
UBOOT_MULTI_H616_VERSION = 2024.01
UBOOT_MULTI_H616_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_MULTI_H616_DL_SUBDIR = uboot
UBOOT_MULTI_H616_SOURCE = u-boot-$(UBOOT_MULTI_H616_VERSION).tar.bz2
UBOOT_MULTI_H616_DEPENDENCIES = host-python3 host-python-setuptools
UBOOT_MULTI_H616_DEPENDENCIES += host-swig host-openssl host-gnutls
UBOOT_MULTI_H616_DEPENDENCIES += arm-trusted-firmware

# Default make opts, adaptation of buildroot uboot's opts. "-I $(HOST_DIR)/include"
# prevents mixing openssl headers from docker (currently 3.0.2) and
# buildroot host-openssl (currently 1.1.1q) which would cause build failures.
UBOOT_MULTI_H616_MAKE_OPTS = \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCC="$(HOSTCC) -I $(HOST_DIR)/include $(subst -I/,-isystem /,$(subst -I /,-isystem /,$(HOST_CFLAGS)))" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)"

# Adjust make opts per target SoC and SoC directories which may
# contain patches and config fragments for SoC.
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
UBOOT_MULTI_H616_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.bin
UBOOT_MULTI_H616_MAKE_OPTS += SCP=/dev/null
UBOOT_MULTI_H616_SOC_DIR = common-h616
else
# Dummy SoC dir prevents adding common level patches twice
# in case a new target SoC starts using this package and
# doesn't define UBOOT_MULTI_H616_SOC_DIR.
UBOOT_MULTI_H616_SOC_DIR = "__DUMMY_DIR__"
endif

# Find any common config fragments and patches in package dir.
UBOOT_MULTI_H616_CNF_FRAGS_COMMON = $(wildcard $(UBOOT_MULTI_H616_PKGDIR)/*.config.fragment)
UBOOT_MULTI_H616_PATCHES_COMMON = $(wildcard $(UBOOT_MULTI_H616_PKGDIR)/*.patch)

# Find any SoC level config fragments and patches in SoC dir (if it exists).
UBOOT_MULTI_H616_CNF_FRAGS_SOC = $(wildcard $(UBOOT_MULTI_H616_PKGDIR)/$(UBOOT_MULTI_H616_SOC_DIR)/*.config.fragment)
UBOOT_MULTI_H616_PATCHES_SOC = $(wildcard $(UBOOT_MULTI_H616_PKGDIR)/$(UBOOT_MULTI_H616_SOC_DIR)/*.patch)

# Use empty extract commands because we extract (and patch, configure, build
# and install) multiple times in a loop.
define UBOOT_MULTI_H616_EXTRACT_CMDS
endef

# Helper macro to extract U-Boot.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTI_H616_STEP_EXTRACT
	@$(call MESSAGE,"Extract U-Boot for $(1)")
	@mkdir -p $(@D)/source-$(1)
	@$(TAR) --strip-components=1 -C $(@D)/source-$(1) $(TAR_OPTIONS) $(UBOOT_MULTI_H616_DL_DIR)/$(UBOOT_MULTI_H616_SOURCE)
endef

# Helper macro to patch U-Boot.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTI_H616_STEP_PATCH
	@$(call MESSAGE,"Patch U-Boot for $(1)")
	$(eval UBOOT_MULTI_H616_PATCHES = $(strip
		$(UBOOT_MULTI_H616_PATCHES_COMMON)
		$(UBOOT_MULTI_H616_PATCHES_SOC)
		$(wildcard $(UBOOT_MULTI_H616_PKGDIR)/$(1)/*.patch)))
	$(if $(UBOOT_MULTI_H616_PATCHES),
		$(foreach patch,$(UBOOT_MULTI_H616_PATCHES),
			$(APPLY_PATCHES) $(@D)/source-$(1) $(dir $(patch)) $(notdir $(patch))
		)
	)
endef

# Helper macro to configure U-Boot, adaptation of buildroot pkg-kconfig's
# config and config fragment handling.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTI_H616_STEP_CONFIGURE
	@$(call MESSAGE,"Configure U-Boot for $(1)")
	$(eval UBOOT_MULTI_H616_CNF_FRAGS = $(strip
		$(UBOOT_MULTI_H616_CNF_FRAGS_COMMON)
		$(UBOOT_MULTI_H616_CNF_FRAGS_SOC)
		$(wildcard $(UBOOT_MULTI_H616_PKGDIR)/$(1)/*.config.fragment)))
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/source-$(1) \
		O=$(@D)/build-$(1) $(UBOOT_MULTI_H616_MAKE_OPTS) $(1)_defconfig
	$(if $(UBOOT_MULTI_H616_CNF_FRAGS),
		support/kconfig/merge_config.sh -m \
			-O $(@D)/build-$(1) $(@D)/build-$(1)/.config \
			$(UBOOT_MULTI_H616_CNF_FRAGS)
		$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/source-$(1) \
			O=$(@D)/build-$(1) $(UBOOT_MULTI_H616_MAKE_OPTS) olddefconfig
	)
endef

# Helper macro to build U-Boot, adaptation of buildroot uboot's build.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTI_H616_STEP_BUILD
	@$(call MESSAGE,"Build U-Boot for $(1)")
	$(TARGET_CONFIGURE_OPTS) \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		PKG_CONFIG_SYSROOT_DIR="/" \
		PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 \
		PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 \
		PKG_CONFIG_LIBDIR="$(HOST_DIR)/lib/pkgconfig:$(HOST_DIR)/share/pkgconfig" \
		$(MAKE) -C $(@D)/source-$(1) \
			O=$(@D)/build-$(1) $(UBOOT_MULTI_H616_MAKE_OPTS) all
endef


# Helper macro to install U-Boot.
# $(1): the name of U-Boot defconfig without _defconfig part
define UBOOT_MULTI_H616_STEP_INSTALL
	@$(call MESSAGE,"Install U-Boot for $(1)")
	@mkdir -p $(BINARIES_DIR)/$(1)
	@$(foreach bin,$(call qstrip,$(BR2_PACKAGE_UBOOT_MULTI_H616_BINARIES)),
		cp -f $(@D)/build-$(1)/$(bin) $(BINARIES_DIR)/$(1)/
	)
endef

# The build loop.
define UBOOT_MULTI_H616_BUILD_CMDS
	$(foreach config,$(call qstrip,$(BR2_PACKAGE_UBOOT_MULTI_H616_CONFIGS)),
		$(call UBOOT_MULTI_H616_STEP_EXTRACT,$(config))
		$(call UBOOT_MULTI_H616_STEP_PATCH,$(config))
		$(call UBOOT_MULTI_H616_STEP_CONFIGURE,$(config))
		$(call UBOOT_MULTI_H616_STEP_BUILD,$(config))
		$(call UBOOT_MULTI_H616_STEP_INSTALL,$(config))
	)
endef

$(eval $(generic-package))
