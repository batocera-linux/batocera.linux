################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 11, 2020
BATOCERA_BEZEL_VERSION = 5fbfc2c10101f46a3437d14eb1e16a661f6d584f
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/* $(TARGET_DIR)/usr/share/batocera/datainit/decorations

	# Decorations
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	echo -e "You can find help here to find how to customize decorations: \n" \
		> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "https://batocera.org/wiki/doku.php?id=en:customize_decorations_bezels" \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
endef

$(eval $(generic-package))
