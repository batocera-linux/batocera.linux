################################################################################
#
# input-wrapper
#
################################################################################
# Version.: Commits on Jan 19, 2024
INPUT_WRAPPER_VERSION = 31985f2e1da8cfcf599a068845ddd3713ba3616c
INPUT_WRAPPER_SITE = $(call github,macromorgan,input-wrapper,$(INPUT_WRAPPER_VERSION))

define INPUT_WRAPPER_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile
endef

define INPUT_WRAPPER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin      $(TARGET_DIR)/etc/init.d
    mkdir -p $(TARGET_DIR)/usr/bin      $(TARGET_DIR)/etc/udev/rules.d

	$(INSTALL) $(@D)/virtual_controller $(TARGET_DIR)/usr/bin/virtual_controller

    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/input-wrapper/sysconfigs/S60input-wrapper         $(TARGET_DIR)/etc/init.d
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/input-wrapper/sysconfigs/99-input-wrapper.rules   $(TARGET_DIR)/etc/udev/rules.d
endef

$(eval $(generic-package))
