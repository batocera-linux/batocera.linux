################################################################################
#
# batocera-configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = 1.4
BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_SETUP_TYPE = pep517
BATOCERA_CONFIGGEN_DEPENDENCIES = \
	host-python-hatchling \
	python-pyyaml \
	python-toml \
	python-evdev \
	python-pyudev \
	python3-configobj \
	python-httplib2 \
	ffmpeg-python \
	python-pillow \
	python-ruamel-yaml
BATOCERA_CONFIGGEN_INSTALL_STAGING = YES

CONFIGGEN_DIR = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen

define BATOCERA_CONFIGGEN_EXTRACT_CMDS
	cp -avf $(CONFIGGEN_DIR)/configgen/* $(@D)
	echo "__version__ = '$(BATOCERA_CONFIGGEN_VERSION)'" > $(@D)/configgen/__version__.py
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2835
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2836
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2837
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2711
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2712
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
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4),y)
	BATOCERA_CONFIGGEN_SYSTEM=s9gen4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
	BATOCERA_CONFIGGEN_SYSTEM=s922x
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2),y)
	BATOCERA_CONFIGGEN_SYSTEM=a3gen2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3328),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3328
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3568),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3568
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3326
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H3),y)
	BATOCERA_CONFIGGEN_SYSTEM=h3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H5),y)
	BATOCERA_CONFIGGEN_SYSTEM=h5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
	BATOCERA_CONFIGGEN_SYSTEM=h616
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	BATOCERA_CONFIGGEN_SYSTEM=s812
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3128
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
	BATOCERA_CONFIGGEN_SYSTEM=odin
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H6),y)
	BATOCERA_CONFIGGEN_SYSTEM=h6
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3588
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110),y)
	BATOCERA_CONFIGGEN_SYSTEM=jh7110
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8250),y)
	BATOCERA_CONFIGGEN_SYSTEM=sm8250
endif

define BATOCERA_CONFIGGEN_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/batocera/configgen
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults.yml \
	    $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml \
	    $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen
	cp -pr $(CONFIGGEN_DIR)/data \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults.yml \
	    $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml \
	    $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
	cp $(CONFIGGEN_DIR)/scripts/call_achievements_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
endef

define BATOCERA_CONFIGGEN_ES_HOOKS
	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/powermode_launch_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/powermode_launch_hooks.sh
endef

define BATOCERA_CONFIGGEN_X86_HOOKS
	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/tdp_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/tdp_hooks.sh

	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/nvidia-workaround.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/nvidia-workaround.sh
endef

BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_ES_HOOKS

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_X86_HOOKS
endif

$(eval $(python-package))
