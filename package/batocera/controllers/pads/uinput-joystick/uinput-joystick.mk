################################################################################
#
# uinput-joystick
#
################################################################################
# Version.: Commits on Feb 11, 2022
UINPUT_JOYSTICK_VERSION = bea7d56f4947b547db2b827640bc9966fe770f84
UINPUT_JOYSTICK_SITE = $(call github,shantigilbert,uinput_joystick,$(UINPUT_JOYSTICK_VERSION))

define UINPUT_JOYSTICK_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) $(UINPUT_JOYSTICK_CFLAGS)" \
		LIBS="$(UINPUT_JOYSTICK_LIBS)" \
		-C $(@D)
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) $(@D)/fftest.c -o $(@D)/fftest
endef

define UINPUT_JOYSTICK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin $(TARGET_DIR)/etc/init.d
	$(INSTALL) $(@D)/uinput_joystick $(TARGET_DIR)/usr/bin/uinput_joystick
	$(INSTALL) $(@D)/fftest          $(TARGET_DIR)/usr/bin/fftest
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/uinput-joystick/S60uinput-joystick $(TARGET_DIR)/etc/init.d
endef

$(eval $(generic-package))
