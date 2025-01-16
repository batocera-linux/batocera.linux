################################################################################
#
# rpigpioswitch 
#
################################################################################
RPIGPIOSWITCH_VERSION = 3.1
RPIGPIOSWITCH_SOURCE =

RPIGPIOSWITCH_SRC = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch

define RPIGPIOSWITCH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/S92switch \
	    $(TARGET_DIR)/etc/init.d/S92switch
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi_gpioswitch.sh \
	    $(TARGET_DIR)/usr/bin/rpi_gpioswitch
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-pin56-power.py \
	    $(TARGET_DIR)/usr/bin/rpi-pin56-power
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-pin356-power.py \
	    $(TARGET_DIR)/usr/bin/rpi-pin356-power
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-retroflag-GPiCase.py \
	    $(TARGET_DIR)/usr/bin/rpi-retroflag-GPiCase
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-retroflag-AdvancedSafeShutdown.py \
	    $(TARGET_DIR)/usr/bin/rpi-retroflag-AdvancedSafeShutdown
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-argonone.py \
	    $(TARGET_DIR)/usr/bin/rpi-argonone
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-kintaro-SafeShutdown.py \
	    $(TARGET_DIR)/usr/bin/rpi-kintaro-SafeShutdown
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/S72gpioinput \
	    $(TARGET_DIR)/etc/init.d/S72gpioinput
endef

# Add Retroflag dtbo for rpi2,3 & 4 boards only
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2836)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2837)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
    define RPIGPIOSWITCH_INSTALL_TARGET_CMDS_POST
	    mkdir -p $(BINARIES_DIR)/retroflag/
	    wget -O $(@D)/RetroFlag_pw_io.dtbo \
		    https://raw.githubusercontent.com/RetroFlag/retroflag-picase/master/RetroFlag_pw_io.dtbo
		$(INSTALL) -D -m 0644 $(@D)/RetroFlag_pw_io.dtbo \
		    $(BINARIES_DIR)/retroflag/
    endef
RPIGPIOSWITCH_POST_INSTALL_TARGET_HOOKS = RPIGPIOSWITCH_INSTALL_TARGET_CMDS_POST
endif

$(eval $(generic-package))
