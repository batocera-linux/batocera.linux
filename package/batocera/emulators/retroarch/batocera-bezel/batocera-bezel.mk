################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 11, 2020
BATOCERA_BEZEL_VERSION = ccc83700dc9fdc23debb15e4f4605de21a75c262
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	(cd $(TARGET_DIR)/usr/share/batocera/datainit/decorations && ln -sf default_unglazed default) # default bezel

	echo -e "You can find help here to find how to customize decorations: \n" \
		> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "https://batocera.org/wiki/doku.php?id=en:customize_decorations_bezels" \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
endef

$(eval $(generic-package))
