################################################################################
#
# xarcade2jstick
#
################################################################################
XARCADE2JSTICK_VERSION = 77ee53f8d6563a40e9def72f74aaf6b73244682e
XARCADE2JSTICK_SITE =  $(call github,petrockblog,xarcade2jstick,$(XARCADE2JSTICK_VERSION))
XARCADE2JSTICK_LICENSE = gpl3
XARCADE2JSTICK_DEPENDENCIES = linux


define XARCADE2JSTICK_BUILD_CMDS
    $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) all
endef

define XARCADE2JSTICK_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/src/xarcade2jstick $(TARGET_DIR)/usr/bin/xarcade2jstick
endef

$(eval $(generic-package))
