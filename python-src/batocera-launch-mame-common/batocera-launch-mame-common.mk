################################################################################
#
# batocera-launch-mame-common
#
################################################################################

BATOCERA_LAUNCH_MAME_COMMON_SETUP_TYPE=hatch
BATOCERA_LAUNCH_MAME_COMMON_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch \
	python-lazy-loader

define BATOCERA_LAUNCH_MAME_COMMON_INSTALL_TARGET_RESOURCES
	mkdir -p $(TARGET_DIR)/usr/share/batocera/launch/data/mame
	$(INSTALL) -D -m 0644 -t $(TARGET_DIR)/usr/share/batocera/launch/data/mame \
		$(@D)/resources/*.toml
endef

BATOCERA_LAUNCH_MAME_COMMON_POST_INSTALL_TARGET_HOOKS += BATOCERA_LAUNCH_MAME_COMMON_INSTALL_TARGET_RESOURCES

$(eval $(local-python-package))
