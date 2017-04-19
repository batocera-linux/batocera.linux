################################################################################
#
# xarcade2jstick
#
################################################################################
#XARCADE2JSTICK_VERSION = fc05aaebd4e07bab26f2f7007b357eb48e0a48c5
#XARCADE2JSTICK_SITE =  $(call github,substring,xarcade2jstick,$(XARCADE2JSTICK_VERSION))
XARCADE2JSTICK_VERSION = a7a93c951b12a81dac8bcd48ef0d760f56c72ba5
XARCADE2JSTICK_SITE =  $(call github,petrockblog,xarcade2jstick,$(XARCADE2JSTICK_VERSION))
XARCADE2JSTICK_LICENSE = gpl3
XARCADE2JSTICK_DEPENDENCIES = linux


define XARCADE2JSTICK_BUILD_CMDS
#    $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) all
    $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define XARCADE2JSTICK_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/src/xarcade2jstick $(TARGET_DIR)/usr/bin/xarcade2jstick
endef

$(eval $(generic-package))
