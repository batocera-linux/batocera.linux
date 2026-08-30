################################################################################
#
# batocera-configgen
#
################################################################################

BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_SETUP_TYPE = hatch
BATOCERA_CONFIGGEN_DEPENDENCIES = \
	python-batocera-common \
	python-toml \
	python-evdev \
	python-pyudev \
	python3-configobj \
	ffmpeg-python \
	python-pillow \
	python-requests \
	python-qrcode \
	pysdl2 \
	batocera-bezel-overlay
BATOCERA_CONFIGGEN_INSTALL_STAGING = YES
BATOCERA_CONFIGGEN_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configgen
BATOCERA_CONFIGGEN_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
BATOCERA_CONFIGGEN_SYSTEM = x86_64
else
BATOCERA_CONFIGGEN_SYSTEM = $(BATOCERA_ARCH)
endif

define BATOCERA_CONFIGGEN_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/batocera/configgen
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/configs/configgen-defaults.yml \
	    $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml \
	    $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen
	cp -pr $(BATOCERA_CONFIGGEN_PKGDIR)/data \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/configs/configgen-defaults.yml \
	    $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml \
	    $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/scripts/call_achievements_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
	# evmapy default hotkeys file
        mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/hotkeys.keys $(TARGET_DIR)/usr/share/evmapy/hotkeys.keys
endef

define BATOCERA_CONFIGGEN_ES_HOOKS
	install -D -m 0755 $(BATOCERA_CONFIGGEN_PKGDIR)/scripts/powermode_launch_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/powermode_launch_hooks.sh
endef

define BATOCERA_CONFIGGEN_X86_HOOKS
	install -D -m 0755 $(BATOCERA_CONFIGGEN_PKGDIR)/scripts/tdp_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/tdp_hooks.sh

	install -D -m 0755 $(BATOCERA_CONFIGGEN_PKGDIR)/scripts/nvidia-workaround.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/nvidia-workaround.sh
endef

define BATOCERA_CONFIGGEN_SCRIPTS
	install -D -m 0755 $(BATOCERA_CONFIGGEN_PKGDIR)/scripts/batocera-joysticks-hotkeys.py \
	    $(TARGET_DIR)/usr/bin/batocera-joysticks-hotkeys
endef

BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_ES_HOOKS
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_SCRIPTS

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_X86_HOOKS
endif

$(eval $(python-package))
