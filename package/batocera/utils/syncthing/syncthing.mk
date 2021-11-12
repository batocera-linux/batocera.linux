################################################################################
#
# syncthing
#
################################################################################

SYNCTHING_VERSION = v1.18.3
SYNCTHING_SITE = $(call github,syncthing,syncthing,$(SYNCTHING_VERSION))
SYNCTHING_LICENSE = MPLv2
SYNCTHING_LICENSE_FILES = LICENSE

SYNCTHING_TARGET_ENV = \
	PATH=$(BR_PATH) \
	GOROOT="$(HOST_GO_ROOT)" \
	GOPATH="$(HOST_GO_GOPATH)" \
	GOCACHE="$(HOST_GO_TARGET_CACHE)"

define SYNCTHING_BUILD_CMDS
	cd $(@D) && $(SYNCTHING_TARGET_ENV) $(GO_BIN) run build.go
endef

define SYNCTHING_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/bin/syncthing $(TARGET_DIR)/usr/bin/syncthing
    $(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/syncthing/S27syncthing       $(TARGET_DIR)/etc/init.d/
endef

$(eval $(golang-package))
