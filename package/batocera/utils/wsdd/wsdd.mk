################################################################################
#
# wsdd
#
################################################################################

WSDD_VERSION = 0.7.1
WSDD_SITE = $(call github,christgau,wsdd,v$(WSDD_VERSION))
WSDD_LICENSE = MIT

define WSDD_INSTALL_TARGET_CMDS
        $(INSTALL) -Dm755 $(@D)/src/wsdd.py $(TARGET_DIR)/usr/bin/wsdd
	mkdir -p $(TARGET_DIR)/etc/init.d
        $(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/wsdd/S93wsdd $(TARGET_DIR)/etc/init.d
endef

$(eval $(generic-package))
