################################################################################
#
# batocera pygame
#
################################################################################

BATOCERA_PYGAME_VERSION = 1.0
BATOCERA_PYGAME_SOURCE=

define BATOCERA_PYGAME_INSTALL_SAMPLE
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-pygame/batocera-pygame $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-pygame/evmapy.keys     $(TARGET_DIR)/usr/share/evmapy/pygame.keys
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-pygame/snake.pygame    $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame

	# create an alias for pygame to be able to kill it with killall and evmapy
	(cd $(TARGET_DIR)/usr/bin && ln -sf python pygame)
endef

BATOCERA_PYGAME_POST_INSTALL_TARGET_HOOKS = BATOCERA_PYGAME_INSTALL_SAMPLE

$(eval $(generic-package))
