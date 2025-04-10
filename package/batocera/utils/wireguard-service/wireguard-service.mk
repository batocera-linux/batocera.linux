################################################################################
#
# wireguard-service
#
################################################################################

WIREGUARD_SERVICE_VERSION = 0.0.1
WIREGUARD_SERVICE_SOURCE =
WIREGUARD_SERVICE_SITE =

WIREGUARD_SERVICE_DEPENDENCIES = wireguard-tools

define WIREGUARD_SERVICE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/etc
	rm -rf $(TARGET_DIR)/etc/wireguard 2>/dev/null || true
	ln -sf /userdata/system/wireguard $(TARGET_DIR)/etc/wireguard
	mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/wireguard-service/wireguard \
	    $(TARGET_DIR)/usr/share/batocera/services/
endef

$(eval $(generic-package))
