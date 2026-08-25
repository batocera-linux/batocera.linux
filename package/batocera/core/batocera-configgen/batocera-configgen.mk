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
	batocera-launch \
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
BATOCERA_CONFIGGEN_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configgen
BATOCERA_CONFIGGEN_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen

	cp -pr $(BATOCERA_CONFIGGEN_PKGDIR)/data \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
	cp $(BATOCERA_CONFIGGEN_PKGDIR)/scripts/call_achievements_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
endef

BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS

$(eval $(python-package))
