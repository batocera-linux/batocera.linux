################################################################################
#
# ryujinx-canary
#
################################################################################

RYUJINX_CANARY_VERSION = 1.3.185
RYUJINX_CANARY_SITE = https://git.ryujinx.app/api/v4/projects/68/packages/generic/Ryubing-Canary/$(RYUJINX_CANARY_VERSION)
RYUJINX_CANARY_LICENSE = MIT
RYUJINX_CANARY_DEPENDENCIES = sdl2 openal hicolor-icon-theme adwaita-icon-theme librsvg

ifeq ($(BR2_x86_64),y)
RYUJINX_CANARY_SOURCE = ryujinx-canary-$(RYUJINX_CANARY_VERSION)-linux_x64.tar.gz
else ifeq ($(BR2_aarch64),y)
RYUJINX_CANARY_SOURCE = ryujinx-canary-$(RYUJINX_CANARY_VERSION)-linux_arm64.tar.gz
endif

define RYUJINX_CANARY_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && \
	    tar xf $(DL_DIR)/$(RYUJINX_CANARY_DL_SUBDIR)/$(RYUJINX_CANARY_SOURCE)
endef

define RYUJINX_CANARY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/ryujinx-canary
	cp -pr $(@D)/target/publish/* $(TARGET_DIR)/usr/ryujinx-canary
endef

$(eval $(generic-package))
