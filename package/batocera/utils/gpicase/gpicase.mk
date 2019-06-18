################################################################################
#
# gpicase
#
################################################################################
GPICASE_VERSION = 1.0
GPICASE_SOURCE = GPi_Case_patch.zip
GPICASE_SITE = http://download.retroflag.com/Products/GPi_Case

define GPICASE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware
	cp package/batocera/utils/gpicase/config_gpicase.txt                $(BINARIES_DIR)/rpi-firmware/config_gpicase.txt
	cp $(@D)/GPi_Case_patch/patch_files/overlays/dpi24.dtbo             $(BINARIES_DIR)/rpi-firmware/overlays/dpi24_gpicase.dtbo
	cp $(@D)/GPi_Case_patch/patch_files/overlays/pwm-audio-pi-zero.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/pwm-audio-pi-zero_gpicase.dtbo
endef

define GPICASE_EXTRACT_CMDS
	$(UNZIP) -d $(@D) $(GPICASE_DL_DIR)/$(GPICASE_SOURCE)
endef

$(eval $(generic-package))
