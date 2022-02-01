################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on Feb 1, 2022
BATOCERA_BEZEL_VERSION = 6a64404e9f0008b737c56c12ba53710d30036d6f
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
	# we don't have all systems with no_curve_night yet, so we copy first the "classic" bezels
	cp -r $(@D)/default_unglazed/*               $(TARGET_DIR)/usr/share/batocera/datainit/decorations/consoles/
	cp -r $(@D)/default_nocurve_night/default.*  $(TARGET_DIR)/usr/share/batocera/datainit/decorations/consoles/
	cp -r $(@D)/default_nocurve_night/systems    $(TARGET_DIR)/usr/share/batocera/datainit/decorations/consoles/
	(cd $(TARGET_DIR)/usr/share/batocera/datainit/decorations && ln -sf consoles default)

	echo -e "You can find help on how to customize decorations: \n" \
		> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "https://wiki.batocera.org/decoration#decoration_bezels_customization" \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "You can put standalone bezels here too." \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt

endef

$(eval $(generic-package))

