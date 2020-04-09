################################################################################
#
# batocera configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = 1.1
BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_DEPENDENCIES = python python-pyyaml
BATOCERA_CONFIGGEN_INSTALL_STAGING = YES

define BATOCERA_CONFIGGEN_EXTRACT_CMDS
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configgen/* $(@D)
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	BATOCERA_CONFIGGEN_SYSTEM=rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	BATOCERA_CONFIGGEN_SYSTEM=rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	BATOCERA_CONFIGGEN_SYSTEM=rpi3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	BATOCERA_CONFIGGEN_SYSTEM=odroidxu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TINKERBOARD),y)
	BATOCERA_CONFIGGEN_SYSTEM=tinkerboard
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
	BATOCERA_CONFIGGEN_SYSTEM=miqi
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_C2),y)
	BATOCERA_CONFIGGEN_SYSTEM=odroidc2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	BATOCERA_CONFIGGEN_SYSTEM=s912
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	BATOCERA_CONFIGGEN_SYSTEM=rockpro64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCK960),y)
	BATOCERA_CONFIGGEN_SYSTEM=rock960
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	BATOCERA_CONFIGGEN_SYSTEM=odroidn2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	BATOCERA_CONFIGGEN_SYSTEM=odroidgoa
endif

define BATOCERA_CONFIGGEN_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/batocera/configgen
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults.yml $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/datainit $(TARGET_DIR)/usr/lib/python2.7/site-packages/configgen/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults.yml $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS

BATOCERA_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
