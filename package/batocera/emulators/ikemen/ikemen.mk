################################################################################
#
# IKEMEN GO
#
################################################################################
# Last commit on Oct 27, 2022
IKEMEN_VERSION = f586e49413c26646642dc3b5039478bd764d386a
IKEMEN_SITE = https://github.com/ikemen-engine/Ikemen-GO
IKEMEN_LICENSE = MIT
IKEMEN_DEPENDENCIES = host-go

IKEMEN_SITE_METHOD = git
IKEMEN_GIT_SUBMODULES = YES

IKEMEN_TARGET_ENV = \
	GOROOT="$(HOST_GO_ROOT)" \
	GOPATH="$(HOST_GO_GOPATH)" \
	PATH=$(BR_PATH) \
    GOCACHE="$(HOST_GO_TARGET_CACHE)" \
	GOMODCACHE="$(@D)" \
	GOFLAGS="-modcacherw" \

define IKEMEN_BUILD_CMDS
	$(IKEMEN_TARGET_ENV) $(MAKE) \
		CPP="$(TARGET_CPP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		AS="$(TARGET_CC)" LD="$(TARGET_LD)" STRIP="$(TARGET_STRIP)" \
		-C $(@D) -f Makefile Ikemen_GO_Linux
endef

define IKEMEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/bin/Ikemen_GO_Linux $(TARGET_DIR)/usr/bin/ikemen
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ikemen/ikemen.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
