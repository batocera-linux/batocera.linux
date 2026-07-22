################################################################################
#
# ikemen
#
################################################################################
# Version: Commits on Feb 5, 2026
IKEMEN_VERSION = ad12c170ed79b5644fe533d3d8eb9784cd58c3e5
IKEMEN_SITE = https://github.com/ikemen-engine/Ikemen-GO
IKEMEN_LICENSE = MIT
IKEMEN_DEPENDENCIES = host-go libgtk3 mesa3d libglfw ffmpeg sdl2
IKEMEN_EMULATOR_INFO = ikemen.emulator.yml

IKEMEN_SITE_METHOD = git
IKEMEN_GIT_SUBMODULES = YES

# kind of dirty workaround for golang-package. Upstream go.mod references
# a deleted pseudo-version (see patch 001). With generic-package, patches
# apply before configure, so fix is possible.

GO_BIN = $(HOST_DIR)/bin/go

IKEMEN_GO_MOD_ENV = \
	$(HOST_GO_COMMON_ENV) \
	GOFLAGS="-modcacherw" \
	GOPROXY="https://proxy.golang.org,direct" \
	GONOSUMCHECK="*" \
	GONOSUMDB="*"

define IKEMEN_CONFIGURE_CMDS
	rm -f $(@D)/go.sum
	cd $(@D) && $(IKEMEN_GO_MOD_ENV) $(GO_BIN) mod tidy
	cd $(@D) && $(IKEMEN_GO_MOD_ENV) $(GO_BIN) mod vendor -v
endef

define IKEMEN_BUILD_CMDS
	cd $(@D) && \
	$(HOST_GO_TARGET_ENV) \
	GOEXPERIMENT=arenas \
	CGO_CFLAGS="$(TARGET_CFLAGS) \
		$$($(HOST_DIR)/bin/pkg-config --cflags libavformat libavcodec libavutil libswscale libswresample libavfilter sdl2)" \
	CGO_LDFLAGS="$(TARGET_LDFLAGS) \
		$$($(HOST_DIR)/bin/pkg-config --libs libavformat libavcodec libavutil libswscale libswresample libavfilter sdl2) \
		-lpthread -lm -ldl -lz" \
	GOFLAGS="-mod=vendor -modcacherw" \
	$(GO_BIN) build -trimpath -v \
		-ldflags "-s -w" \
		-o $(@D)/bin/Ikemen_GO_Linux \
		./src
endef

define IKEMEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/bin/Ikemen_GO_Linux $(TARGET_DIR)/usr/bin/ikemen
	# evmapy
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ikemen/ikemen.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
