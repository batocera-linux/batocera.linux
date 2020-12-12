################################################################################
#
# rpigpioswitch 
#
################################################################################
RPIGPIOSWITCH_VERSION = 1.0
RPIGPIOSWITCH_SOURCE =

define RPIGPIOSWITCH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/S92switch                             $(TARGET_DIR)/etc/init.d/S92switch
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi_gpioswitch.sh                     $(TARGET_DIR)/usr/bin/rpi_gpioswitch
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-pin56-power.py                    $(TARGET_DIR)/usr/bin/rpi-pin56-power
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-pin356-power.py                   $(TARGET_DIR)/usr/bin/rpi-pin356-power
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-retroflag-SafeShutdown.py         $(TARGET_DIR)/usr/bin/rpi-retroflag-SafeShutdown
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-retroflag-GPiCase.py              $(TARGET_DIR)/usr/bin/rpi-retroflag-GPiCase
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-retroflag-AdvancedSafeShutdown.py $(TARGET_DIR)/usr/bin/rpi-retroflag-AdvancedSafeShutdown
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-argonone.py                       $(TARGET_DIR)/usr/bin/rpi-argonone
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/rpi-kintaro-SafeShutdown.py           $(TARGET_DIR)/usr/bin/rpi-kintaro-SafeShutdown
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/rpigpioswitch/S72gpioinput                          $(TARGET_DIR)/etc/init.d/S72gpioinput
endef

$(eval $(generic-package))
