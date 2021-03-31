################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Nov 10, 2020
BATOCERA_BEZEL_VERSION = 5d7e7fa352d9dac775877fb63f2be5d8f40dd4ce
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_broadcast 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_gameroom 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_monitor_1084s    $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_night 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_vintage_tv	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_1980s  	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_1980s_vertical     $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_vertical_default   $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/default_unglazed          $(TARGET_DIR)/usr/share/batocera/datainit/decorations

	(cd $(TARGET_DIR)/usr/share/batocera/datainit/decorations && ln -sf default_unglazed default) # default bezel

	echo -e "You can find help here to find how to customize decorations: \n" \
		> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "https://batocera.org/wiki/doku.php?id=en:customize_decorations_bezels" \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "You can put zip standalone bezels here too." \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt

endef

$(eval $(generic-package))
