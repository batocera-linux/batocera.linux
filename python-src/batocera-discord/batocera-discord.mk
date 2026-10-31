################################################################################
#
# batocera-discord
#
################################################################################

BATOCERA_DISCORD_VERSION = 44.0
BATOCERA_DISCORD_LICENSE = GPL
BATOCERA_DISCORD_SETUP_TYPE = hatch
BATOCERA_DISCORD_DEPENDENCIES = python3 python-pygame2 python-evdev python-qrcode

define BATOCERA_DISCORD_INSTALL_SERVICE
	$(INSTALL) -D -m 0755 $(@D)/resources/discord.service $(TARGET_DIR)/usr/share/batocera/services/discord
endef

BATOCERA_DISCORD_POST_INSTALL_TARGET_HOOKS += BATOCERA_DISCORD_INSTALL_SERVICE

$(eval $(local-python-package))
