################################################################################
#
# batocera configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = 1.0
BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_DEPENDENCIES = python python-pyyaml

define BATOCERA_CONFIGGEN_EXTRACT_CMDS
	cp -R package/batocera/core/batocera-configgen/configgen/* $(@D)
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	BATOCERA_CONFIGGEN_SYSTEM=rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	BATOCERA_CONFIGGEN_SYSTEM=rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	BATOCERA_CONFIGGEN_SYSTEM=rpi3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
	BATOCERA_CONFIGGEN_SYSTEM=xu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_C2),y)
	BATOCERA_CONFIGGEN_SYSTEM=c2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	BATOCERA_CONFIGGEN_SYSTEM=s912
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86)$(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	BATOCERA_CONFIGGEN_SYSTEM=rockpro64
endif

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/recalbox/system/configgen
	cp package/batocera/core/batocera-configgen/configs/configgen-defaults.yml $(TARGET_DIR)/recalbox/system/configgen/configgen-defaults.yml
	cp package/batocera/core/batocera-configgen/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml $(TARGET_DIR)/recalbox/system/configgen/configgen-defaults-arch.yml
endef
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS

BATOCERA_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
