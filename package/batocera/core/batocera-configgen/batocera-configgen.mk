################################################################################
#
# batocera configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = 1.4
BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_DEPENDENCIES = python3 python-pyyaml
BATOCERA_CONFIGGEN_INSTALL_STAGING = YES

define BATOCERA_CONFIGGEN_EXTRACT_CMDS
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configgen/* $(@D)
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2835
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2836
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2837
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2711
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	BATOCERA_CONFIGGEN_SYSTEM=odroidxu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN2),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905gen2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905gen3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	BATOCERA_CONFIGGEN_SYSTEM=s912
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
	BATOCERA_CONFIGGEN_SYSTEM=s922x
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3328),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3328
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3568),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3568
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3326
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TRITIUM_H5),y)
	BATOCERA_CONFIGGEN_SYSTEM=tritium-h5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2),y)
	BATOCERA_CONFIGGEN_SYSTEM=orangepi-zero2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
	BATOCERA_CONFIGGEN_SYSTEM=orangepi-pc
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	BATOCERA_CONFIGGEN_SYSTEM=cha
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	BATOCERA_CONFIGGEN_SYSTEM=s812
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3128
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
	BATOCERA_CONFIGGEN_SYSTEM=odin
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_3_LTS),y)
	BATOCERA_CONFIGGEN_SYSTEM=orangepi-3-lts
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3588
endif

define BATOCERA_CONFIGGEN_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/batocera/configgen
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults.yml $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/data $(TARGET_DIR)/usr/share/batocera/configgen/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults.yml $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef

define BATOCERA_CONFIGGEN_BINS
        chmod a+x $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/emulatorlauncher.py
        (mkdir -p $(TARGET_DIR)/usr/bin/ && cd $(TARGET_DIR)/usr/bin/ && ln -sf /usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/emulatorlauncher.py emulatorlauncher)
endef

BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_BINS

BATOCERA_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
