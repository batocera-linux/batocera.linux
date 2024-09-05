################################################################################
#
# syncthing
#
################################################################################

SYNCTHING_VERSION = v1.27.10
SYNCTHING_SITE = $(call github,syncthing,syncthing,$(SYNCTHING_VERSION))
SYNCTHING_LICENSE = MPLv2
SYNCTHING_LICENSE_FILES = LICENSE

ifeq ($(BR2_arm),y)
    GOARCH= arm
endif
ifeq ($(BR2_aarch64),y)
    GOARCH=arm64
endif
ifeq ($(BR2_x86_64),y)
    GOARCH=amd64
endif
ifeq ($(BR2_riscv),y)
    GOARCH=riscv64
endif

# GOFLAGS="-modcacherw" used to fix directory permissions to make sure cleanbuild works.
# For details see: 
# https://github.com/golang/go/issues/27161 https://github.com/golang/go/issues/27455

SYNCTHING_TARGET_ENV = \
	GOROOT="$(HOST_GO_ROOT)" \
	GOPATH="$(HOST_GO_GOPATH)" \
	PATH=$(BR_PATH) \
    GOCACHE="$(HOST_GO_TARGET_CACHE)" \
	GOMODCACHE="$(@D)" \
	GOFLAGS="-modcacherw" \

define SYNCTHING_BUILD_CMDS
	cd $(@D) && $(SYNCTHING_TARGET_ENV) \
	    $(GO_BIN) run build.go -goos linux -goarch $(GOARCH) build
endef

define SYNCTHING_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	$(INSTALL) -D $(@D)/syncthing $(TARGET_DIR)/usr/bin/syncthing
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/syncthing/syncthing \
	    $(TARGET_DIR)/usr/share/batocera/services/
endef

$(eval $(golang-package))
