################################################################################
#
# FUN R1 Gamepad Controller Driver
#
################################################################################
# Version.: Commits on July 6, 2022
FUN_R1_GAMEPAD_VERSION = 1
FUN_R1_GAMEPAD_SOURCE =
FUN_R1_GAMEPAD_LICENSE = GPLv2

FUN_R1_GAMEPAD_FLAGS=

define FUN_R1_GAMEPAD_BUILD_CMDS
	$(TARGET_CC) $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/fun-r1-gamepad/fun_r1_gamepad.c -o $(@D)/fun_r1_gamepad
endef

define FUN_R1_GAMEPAD_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/fun_r1_gamepad $(TARGET_DIR)/usr/bin/fun_r1_gamepad
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/fun-r1-gamepad/S31funr1gamepad $(TARGET_DIR)/etc/init.d/S31funr1gamepad
endef

$(eval $(generic-package))
