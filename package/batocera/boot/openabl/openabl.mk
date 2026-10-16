################################################################################
#
# openabl
#
################################################################################

OPENABL_VERSION = 1.0
OPENABL_SOURCE = openabl-v$(OPENABL_VERSION)-source.tar.xz
OPENABL_SITE = https://github.com/OpenHandheldCollective/OpenABL/releases/download/v$(OPENABL_VERSION)
OPENABL_LICENSE = GPL-3.0+
OPENABL_LICENSE_FILES = LICENSE LICENSES.md
OPENABL_DEPENDENCIES = host-clang host-lld host-python3 host-python-setuptools \
	host-python-cryptography host-util-linux pv

OPENABL_CHIPSET = $(BATOCERA_ARCH)
OPENABL_IMAGE = abl_signed-$(call UPPERCASE,$(OPENABL_CHIPSET)).elf

# Per-chipset settings from upstream's build.sh
OPENABL_SIGN = -v7
OPENABL_PARAMS = PVMFW_ENABLED=true DISABLE_KERNEL_PROTOCOL=0 ABL_LARGE_IMAGE=1
OPENABL_SOC_FEATURES =
OPENABL_STANDARD_BOOT_FEATURES = standard-boot card-logo

ifeq ($(OPENABL_CHIPSET),sm4450)
OPENABL_SOC_FEATURES = sdcc-sm4450
else ifeq ($(OPENABL_CHIPSET),sm6115)
OPENABL_SIGN = -v6
OPENABL_PARAMS = PVMFW_ENABLED=false DISABLE_KERNEL_PROTOCOL=0 ABL_LARGE_IMAGE=1 \
	ABL_USB_HOST_BUNDLED_STACK=1 TARGET_SOC_SM6115=1
OPENABL_SOC_FEATURES = loader-quirks
else ifeq ($(OPENABL_CHIPSET),sm8250)
OPENABL_SIGN = -v6
OPENABL_PARAMS = PVMFW_ENABLED=false DISABLE_KERNEL_PROTOCOL=0
else ifeq ($(OPENABL_CHIPSET),sm8750)
OPENABL_STANDARD_BOOT_FEATURES += sysfont
endif

OPENABL_FEATURES = \
	$(if $(BR2_PACKAGE_OPENABL_STANDARD_BOOT),$(OPENABL_STANDARD_BOOT_FEATURES)) \
	$(OPENABL_SOC_FEATURES) \
	$(if $(BR2_PACKAGE_OPENABL_ZH_HANS),zh-hans) \
	$(if $(BR2_PACKAGE_OPENABL_DEBUG),debug)

OPENABL_PARAMS += \
	PREBUILT_HOST_TOOLS="BUILD_CC=$(HOSTCC_NOCCACHE) BUILD_CXX=$(HOSTCXX_NOCCACHE) EXTRA_OPTFLAGS=-Wno-error COPT=-std=gnu17" \
	QSPA_BOOTCONFIG_ENABLE=0 AB_RETRYCOUNT_DISABLE=0 VERIFIED_BOOT_ENABLED=1 \
	USER_BUILD_VARIANT=1 DISABLE_PARALLEL_DOWNLOAD_FLASH=0 TARGET_ARCHITECTURE=arm64 \
	CLANG_PREFIX=$(TARGET_CROSS) BOARD_BOOTLOADER_PRODUCT_NAME=OpenABL \
	BOARD_BOOTLOADER_PRODUCT_VERSION=$(OPENABL_VERSION) REMOVE_CARVEOUT_REGION=0 \
	ABL_USB_HOST=1 OPENABL_MENU=1

# bin/ holds the unwrapped host clang (buildroot's wrapper adds the target's
# tuning flags) and the cross ld under the name clang looks for.
OPENABL_ENV = $(TARGET_MAKE_ENV) PATH=$(@D)/bin:$(BR_PATH) \
	PYTHON_COMMAND=$(HOST_DIR)/bin/python3

# Qualcomm's code is warning-clean only on upstream's older clang.
define OPENABL_APPLY_ABL_PATCH
	$(APPLY_PATCHES) $(@D)/build/edk2 $(@D)/Abl openabl.patch
	cp -R $(@D)/Abl/QcomModulePkg/. $(@D)/build/edk2/QcomModulePkg/
	sed -i 's/^\(DEFINE CLANG35_WARNING_OVERRIDES *=[^\r]*\)/\1 -Wno-error/' \
		$(@D)/build/edk2/BaseTools/Conf/tools_def.template
endef
OPENABL_POST_PATCH_HOOKS += OPENABL_APPLY_ABL_PATCH

define OPENABL_BUILD_CMDS
	mkdir -p $(@D)/bin $(@D)/build/edk2/QcomModulePkg/Prebuilt/OpenAblMenu $(@D)/build/out
	ln -sf $(HOST_DIR)/bin/clang.br_real $(@D)/bin/clang
	ln -sf $(TARGET_LD) $(@D)/bin/aarch64-linux-gnu-ld
	$(OPENABL_ENV) $(MAKE) -C $(@D) LD=lld-link PYTHON=$(HOST_DIR)/bin/python3 \
		FEATURES=$(subst $(space),$(comma),$(strip $(OPENABL_FEATURES))) \
		OUT=build/menu
	cp $(@D)/build/menu/openabl-menu.efi $(@D)/build/edk2/QcomModulePkg/Prebuilt/OpenAblMenu/
	cd $(@D)/build/edk2 && $(OPENABL_ENV) \
		EXTRA_LDFLAGS="-L$(HOST_DIR)/lib -Wl,-rpath,$(HOST_DIR)/lib" bash -c '. ./edksetup.sh --reconfig && \
		$(MAKE1) all $(OPENABL_PARAMS)'
	$(HOST_DIR)/bin/python3 $(@D)/build/qtestsign/qtestsign.py $(OPENABL_SIGN) \
		-o $(@D)/build/out/$(OPENABL_IMAGE) abl $(@D)/build/edk2/unsigned_abl.elf
	cd $(@D)/build/out && sha256sum $(OPENABL_IMAGE) > $(OPENABL_IMAGE).sha256
endef

define OPENABL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/build/out/$(OPENABL_IMAGE) \
		$(TARGET_DIR)/usr/share/bootloader/openabl/$(OPENABL_IMAGE)
	$(INSTALL) -D -m 0644 $(@D)/build/out/$(OPENABL_IMAGE).sha256 \
		$(TARGET_DIR)/usr/share/bootloader/openabl/$(OPENABL_IMAGE).sha256
	echo v$(OPENABL_VERSION) > $(TARGET_DIR)/usr/share/bootloader/openabl/version
	$(INSTALL) -D -m 0755 $(OPENABL_PKGDIR)/updateabl $(TARGET_DIR)/usr/bin/updateabl
endef

$(eval $(generic-package))
