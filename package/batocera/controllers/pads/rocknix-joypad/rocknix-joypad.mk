################################################################################
#
# rocknix-joypad
#
################################################################################
# Version: Commits on Nov 22, 2025
ROCKNIX_JOYPAD_VERSION = 15b5a29b6b24c0fc59dd6f61602dacf34cbb7eae
ROCKNIX_JOYPAD_SITE = $(call github,ROCKNIX,rocknix-joypad,$(ROCKNIX_JOYPAD_VERSION))
ROCKNIX_JOYPAD_DEPENDENCIES = 

ROCKNIX_JOYPAD_USER_EXTRA_CFLAGS = -w -Wno-error=unused-function

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
ROCKNIX_JOYPAD_DEVICE_NAME = RK3588
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
ROCKNIX_JOYPAD_DEVICE_NAME = S922X
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H700),y)
ROCKNIX_JOYPAD_DEVICE_NAME = H700
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
ROCKNIX_JOYPAD_DEVICE_NAME = RK3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
ROCKNIX_JOYPAD_DEVICE_NAME = RK3326
else
ROCKNIX_JOYPAD_DEVICE_NAME = 
endif

ROCKNIX_JOYPAD_MODULE_MAKE_OPTS = \
	DEVICE=$(ROCKNIX_JOYPAD_DEVICE_NAME) \
	KCFLAGS="$$KCFLAGS $(ROCKNIX_JOYPAD_USER_EXTRA_CFLAGS)"

$(eval $(kernel-module))
$(eval $(generic-package))
