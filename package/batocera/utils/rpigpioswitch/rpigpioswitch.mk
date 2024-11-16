################################################################################
#
# rpigpioswitch 
#
################################################################################
RPIGPIOSWITCH_VERSION = 2.9
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
	$(INSTALL) -D -m 0755 $(RPIGPIOSWITCH_SRC)/rpi-retroflag-SafeShutdown.py \
	    $(TARGET_DIR)/usr/bin/rpi-retroflag-SafeShutdown
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

$(eval $(generic-package))
