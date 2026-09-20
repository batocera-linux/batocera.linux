################################################################################
#
# batocera-launch-mame
#
################################################################################

BATOCERA_LAUNCH_MAME_SETUP_TYPE = hatch
BATOCERA_LAUNCH_MAME_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch \
	batocera-launch-mame-common

ifneq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),)
define BATOCERA_LAUNCH_MAME_INSTALL_XORG_SCRIPTS
	# gameStop script when exiting a rotated screen (xorg)
	mkdir -p $(TARGET_DIR)/usr/share/batocera/launch/scripts

	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/share/batocera/launch/scripts \
		$(@D)/resources/scripts/rotation_fix.sh
endef

BATOCERA_LAUNCH_MAME_POST_INSTALL_TARGET_HOOKS += BATOCERA_LAUNCH_MAME_INSTALL_XORG_SCRIPTS
endif

$(eval $(local-python-package))
