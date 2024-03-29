################################################################################
#
# wsdd-native
#
################################################################################

WSDD_NATIVE_VERSION = 1.8
WSDD_NATIVE_SITE = $(call github,gershnik,wsdd-native,v$(WSDD_NATIVE_VERSION))
WSDD_NATIVE_LICENSE = BSD

WSDD_NATIVE_DEPENDENCIES += host-cmake
WSDD_NATIVE_CONF_OPTS += -DWSDDN_PREFER_SYSTEM=OFF -DWSDDN_WITH_SYSTEMD="no" -DCMAKE_BUILD_TYPE=Release

define WSDD_NATIVE_INSTALL_TARGET_CMDS
        $(INSTALL) -Dm755 $(@D)/wsddn $(TARGET_DIR)/usr/bin/wsdd
        $(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/wsdd/S93wsdd $(TARGET_DIR)/etc/init.d
endef

$(eval $(cmake-package))
