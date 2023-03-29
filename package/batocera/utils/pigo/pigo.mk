################################################################################
#
# pigo
#
################################################################################

PIGO_VERSION = v1.4.6
PIGO_SITE = $(call github,esimov,pigo,$(PIGO_VERSION))
PIGO_LICENSE = MIT
PIGO_EXTRA_ARGS = 

ifeq ($(BR2_arm),y)
    PIGO_EXTRA_ARGS += ARCH=aarch32
else ifeq ($(BR2_aarch64),y)
    PIGO_EXTRA_ARGS += ARCH=aarch64
endif

ifeq ($(BR2_x86_64),y)
    PIGO_EXTRA_ARGS += ARCH=X86_64
endif

HOST_GO_COMMON_ENV = GOFLAGS=-mod=mod \
		     GO111MODULE=on \
		     GOROOT="$(HOST_GO_ROOT)" \
		     GOPATH="$(HOST_GO_GOPATH)" \
		     GOCACHE="$(HOST_GO_TARGET_CACHE)" \
		     GOMODCACHE="$(@D)" \
		     GOFLAGS="-modcacherw" \
		     PATH=$(BR_PATH) \
		     GOBIN= \
		     CGO_ENABLED=$(HOST_GO_CGO_ENABLED)

define PIGO_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) $(PIGO_EXTRA_ARGS) -C $(@D)
endef

define PIGO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/pigo $(TARGET_DIR)/usr/bin/pigo
endef

$(eval $(generic-package))
