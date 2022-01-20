################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Dec 30, 2021
BATOCERA_BEZEL_VERSION = c352cb979f5b1523f411a9db2c16575d97f05daf
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
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations/consoles
	cp -r $(@D)/default_unglazed/*        $(TARGET_DIR)/usr/share/batocera/datainit/decorations/consoles/
	cp -r $(@D)/default_nocurve_night/*   $(TARGET_DIR)/usr/share/batocera/datainit/decorations/consoles/

	# (cd $(TARGET_DIR)/usr/share/batocera/datainit/decorations && ln -sf default_nocurve_night default) # not every system yet, hence the previous 2 lines

	echo -e "You can find help on how to customize decorations: \n" \
		> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "https://wiki.batocera.org/decoration#decoration_bezels_customization" \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "You can put standalone bezels here too." \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt

endef

$(eval $(generic-package))

