################################################################################
#
# syncthing
#
################################################################################

SYNCTHING_VERSION = v1.18.4
SYNCTHING_SITE = $(call github,syncthing,syncthing,$(SYNCTHING_VERSION))
SYNCTHING_LICENSE = MPLv2
SYNCTHING_LICENSE_FILES = LICENSE

ifeq ($(BR2_arm),y)
    ifeq ($(BR2_cortex_a7),y)
                GOARCH= arm
    else ifeq ($(BR2_cortex_a9),y)
                GOARCH= arm
    else ifeq ($(BR2_cortex_a15),y)
                GOARCH= arm
    else ifeq ($(BR2_cortex_a17),y)
                GOARCH= arm
    else ifeq ($(BR2_cortex_a53),y)
                GOARCH= arm
    endif
endif
ifeq ($(BR2_aarch64),y)
GOARCH=arm64
endif
ifeq ($(BR2_x86_64),y)
GOARCH=amd64
endif

SYNCTHING_TARGET_ENV = \
	PATH=$(BR_PATH) \
	CGO_ENABLED=1 \
	GOCACHE="$(HOST_GO_TARGET_CACHE)" \
	GOMODCACHE="$(@D)" \
	CC_FOR_TARGET="$(TARGET_CC)" \
	CXX_FOR_TARGET="$(TARGET_CXX)"

define SYNCTHING_BUILD_CMDS
	cd $(@D) && $(SYNCTHING_TARGET_ENV) $(GO_BIN) run build.go -goos linux -goarch $(GOARCH) build
endef

define SYNCTHING_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/etc/init.d
	$(INSTALL) -D $(@D)/syncthing $(TARGET_DIR)/usr/bin/syncthing
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/syncthing/S27syncthing       $(TARGET_DIR)/etc/init.d/
endef

$(eval $(golang-package))
