################################################################################
#
# batocera bezel
#
################################################################################
# Version.: Commits on May 11, 2020
BATOCERA_BEZEL_VERSION = dce5a3a507daf700a97f44fed44eeb6defed16c6
BATOCERA_BEZEL_SITE = $(call github,batocera-linux,batocera-bezel,$(BATOCERA_BEZEL_VERSION))

define BATOCERA_BEZEL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_01 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_02 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_03 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_04 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_05 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_06 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_07 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_08 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_09 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_10 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_11 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_12 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_13 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_14 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_15 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_16 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_17 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_18 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_19 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/ambiance_20 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_01   	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_02   	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_vertical_01 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_vertical_02 	      $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/arcade_vertical_default   $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/atomiswave_naomi_vertical $(TARGET_DIR)/usr/share/batocera/datainit/decorations
	cp -r $(@D)/default_unglazed          $(TARGET_DIR)/usr/share/batocera/datainit/decorations

	(cd $(TARGET_DIR)/usr/share/batocera/datainit/decorations && ln -sf default_unglazed default) # default bezel

	echo -e "You can find help here to find how to customize decorations: \n" \
		> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
	echo "https://batocera.org/wiki/doku.php?id=en:customize_decorations_bezels" \
		>> $(TARGET_DIR)/usr/share/batocera/datainit/decorations/readme.txt
endef

$(eval $(generic-package))
