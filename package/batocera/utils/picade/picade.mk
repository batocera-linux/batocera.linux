################################################################################
#
# picade
#
################################################################################
# Version.: Commits on Sep 8, 2025
PICADE_VERSION = f97c2ac7211c8d9ff866b22a82c3b2ae6d01e0df
PICADE_SITE = $(call github,pimoroni,picade-hat,$(PICADE_VERSION))
PICADE_INSTALL_IMAGES = YES
PICADE_DEPENDENCIES += host-dtc

define PICADE_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D)
endef

define PICADE_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
    cp $(@D)/picade.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/picade.dtbo
endef

$(eval $(generic-package))
