################################################################################
#
# picade
#
################################################################################
# Version.: Commits on Mar 5, 2020
PICADE_VERSION = df02844c0cd773af5b908f47eac5fb1f7f361531
PICADE_SITE = $(call github,pimoroni,picade-hat,$(PICADE_VERSION))

# These commands do not build correctly. Working around by manually copying and pasting the file for now.
#define PICADE_BUILD_CMDS
#    cd $(@D)
#    $(MAKE)
#endef

define PICADE_INSTALL_TARGET_CMDS
    mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
    #cp $(@D)/picade.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/picade.dtbo
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/picade/picade.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/picade.dtbo
endef

$(eval $(generic-package))
