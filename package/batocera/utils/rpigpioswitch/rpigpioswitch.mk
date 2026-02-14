################################################################################
#
# rpigpioswitch
#
################################################################################
RPIGPIOSWITCH_VERSION = 3.3
RPIGPIOSWITCH_SOURCE =

define RPIGPIOSWITCH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/S92switch \
	    $(TARGET_DIR)/etc/init.d/S92switch
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi_gpioswitch.sh \
	    $(TARGET_DIR)/usr/bin/rpi_gpioswitch
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-pin56-power.py \
	    $(TARGET_DIR)/usr/bin/rpi-pin56-power
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-pin356-power.py \
	    $(TARGET_DIR)/usr/bin/rpi-pin356-power
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-retroflag-64PiCase.py \
	    $(TARGET_DIR)/usr/bin/rpi-retroflag-64PiCase
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-retroflag-GPiCase.py \
	    $(TARGET_DIR)/usr/bin/rpi-retroflag-GPiCase
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-retroflag-AdvancedSafeShutdown.py \
	    $(TARGET_DIR)/usr/bin/rpi-retroflag-AdvancedSafeShutdown
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-argonone.py \
	    $(TARGET_DIR)/usr/bin/rpi-argonone
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/rpi-kintaro-SafeShutdown.py \
	    $(TARGET_DIR)/usr/bin/rpi-kintaro-SafeShutdown
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_PKGDIR)/S72gpioinput \
	    $(TARGET_DIR)/etc/init.d/S72gpioinput
endef

# Add Retroflag dtbo for rpi2,3 & 4 boards only
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2836)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2837)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
RPIGPIOSWITCH_EXTRA_DOWNLOADS = https://raw.githubusercontent.com/RetroFlag/retroflag-picase/master/RetroFlag_pw_io.dtbo
RPIGPIOSWITCH_INSTALL_IMAGES = YES

define RPIGPIOSWITCH_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/retroflag/
	$(INSTALL) -D -m 0644 $(RPIGPIOSWITCH_DL_DIR)/RetroFlag_pw_io.dtbo $(BINARIES_DIR)/retroflag/
endef
endif

$(eval $(generic-package))
