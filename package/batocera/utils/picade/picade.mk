################################################################################
#
# picade
#
################################################################################
# Version.: Commits on Mar 5, 2020
PICADE_VERSION = df02844c0cd773af5b908f47eac5fb1f7f361531
PICADE_SITE = $(call github,pimoroni,picade-hat,$(PICADE_VERSION))

define PICADE_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D)
endef

define PICADE_INSTALL_TARGET_CMDS
    mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
    cp $(@D)/picade.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/picade.dtbo
endef

$(eval $(generic-package))
