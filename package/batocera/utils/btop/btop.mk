################################################################################
#
# btop
#
################################################################################

BTOP_VERSION = v1.2.6
BTOP_SITE = $(call github,aristocratos,btop,$(BTOP_VERSION))
BTOP_LICENSE = Apache-2.0
BTOP_DEPENDENCIES = 

define BTOP_BUILD_CMDS
	cd $(@D); $(MAKE)
endef

define BTOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/btop

	$(INSTALL) -D $(@D)/bin/btop $(TARGET_DIR)/usr/bin/btop
	cp -prn $(@D)/themes $(TARGET_DIR)/usr/share/btop/
endef

$(eval $(generic-package))
