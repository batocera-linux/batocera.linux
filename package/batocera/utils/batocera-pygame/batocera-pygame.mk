################################################################################
#
# batocera pygame
#
################################################################################

BATOCERA_PYGAME_VERSION = e3238c736dfbde20d7ee402828ec57d89586d4de
RETROTRIVIA_VERSION = 1.3
BATOCERA_PYGAME_LICENSE = GPLv3
BATOCERA_PYGAME_SITE = $(call github,lbrpdx,retrotrivia,$(BATOCERA_PYGAME_VERSION))

define BATOCERA_PYGAME_INSTALL_SAMPLE
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-pygame/evmapy.keys     $(TARGET_DIR)/usr/share/evmapy/pygame.keys
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/assets
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/images/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/manuals/
	$(INSTALL) -D -m 0755 $(@D)/retrotrivia.pygame $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	$(INSTALL) -D -m 0644 $(@D)/questions.py       $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	$(INSTALL) -D -m 0644 $(@D)/videoplayer.py     $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	$(INSTALL) -D -m 0644 $(@D)/gamelists.py       $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	$(INSTALL) -D -m 0644 $(@D)/gamelists.py       $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	$(INSTALL) -D -m 0644 $(@D)/assets/*           $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/assets/
	$(INSTALL) -D -m 0644 $(@D)/README.md          $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/retrotrivia/
	$(INSTALL) -D -m 0644 $(@D)/retrotrivia.png        $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/images
	$(INSTALL) -D -m 0644 $(@D)/retrotrivia-manual.pdf $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/manuals
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-pygame/retrotrivia.xml        $(TARGET_DIR)/usr/share/batocera/datainit/roms/pygame/gamelist.xml

	# create an alias for pygame to be able to kill it with killall and evmapy
	(cd $(TARGET_DIR)/usr/bin && ln -sf python pygame)
endef

BATOCERA_PYGAME_POST_INSTALL_TARGET_HOOKS = BATOCERA_PYGAME_INSTALL_SAMPLE

$(eval $(generic-package))
