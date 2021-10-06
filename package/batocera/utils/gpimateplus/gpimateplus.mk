################################################################################
#
# gpimate+ cm4 module for retroflag gpicase
#
################################################################################
GPIMATEPLUS_VERSION = 1.0
GPIMATEPLUS_SOURCE = disable-pcie.dtbo
GPIMATEPLUS_SITE = https://github.com/martinx72/GPiMatePlusHowTo/raw/main

define GPIMATEPLUS_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	cp $(@D)/disable-pcie.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/disable-pcie.dtbo
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/gpimateplus/S92gpimateplus $(TARGET_DIR)/etc/init.d/S92gpimateplus
endef

define GPIMATEPLUS_EXTRACT_CMDS
        mv $(GPIMATEPLUS_DL_DIR)/$(GPIMATEPLUS_SOURCE) $(@D)/
endef

$(eval $(generic-package))
