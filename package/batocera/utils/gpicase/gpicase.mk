################################################################################
#
# gpicase
#
################################################################################
GPICASE_VERSION = 2.0
GPICASE_SOURCE = GPi_Case_patch.zip
GPICASE_SITE = https://support.retroflag.com/Products/GPi_Case

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
BATOCERA_RPI_VIDEO = vcore
else ifeq ($(BR2_PACKAGE_MESA3D),y)
BATOCERA_RPI_VIDEO = mesa3d
endif

define GPICASE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	cp $(@D)/GPi_Case_patch/patch_files/overlays/dpi24.dtbo                                                 $(BINARIES_DIR)/rpi-firmware/overlays/dpi24_gpicase.dtbo
	cp $(@D)/GPi_Case_patch/patch_files/overlays/pwm-audio-pi-zero.dtbo                                     $(BINARIES_DIR)/rpi-firmware/overlays/pwm-audio-pi-zero_gpicase.dtbo
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/gpicase/99-gpicase.rules                        $(TARGET_DIR)/etc/udev/rules.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/gpicase/batocera-$(BATOCERA_RPI_VIDEO)-install  $(TARGET_DIR)/usr/bin/batocera-gpicase-install
endef

define GPICASE_EXTRACT_CMDS
	$(UNZIP) -d $(@D) $(GPICASE_DL_DIR)/$(GPICASE_SOURCE)
        mv $(@D)/GPi_Case_patch $(@D)/GPi_Case_patch_parent
	mv $(@D)/GPi_Case_patch_parent/* $(@D)/
	rmdir $(@D)/GPi_Case_patch_parent
endef

$(eval $(generic-package))
