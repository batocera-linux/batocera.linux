################################################################################
#
# Rclone
#
################################################################################

RCLONE_VERSION = v1.58.0
RCLONE_SITE = $(call github,rclone,rclone,$(RCLONE_VERSION))
RCLONE_LICENSE = GPLv2
RCLONE_DEPENDENCIES = 

RCLONE_TARGET_ENV = \
	PATH=$(BR_PATH) \
	GOROOT="$(HOST_GO_ROOT)" \
	GOPATH="$(HOST_GO_GOPATH)" \
	GOCACHE="$(HOST_GO_TARGET_CACHE)"

define RCLONE_BUILD_CMDS
	cd $(@D) && $(RCLONE_TARGET_ENV) $(GO_BIN) build
endef

define RCLONE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/rclone $(TARGET_DIR)/usr/bin/rclone
endef

$(eval $(golang-package))
