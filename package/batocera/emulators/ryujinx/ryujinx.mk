################################################################################
#
# ryujinx
#
################################################################################

RYUJINX_VERSION = 1.2.86
RYUJINX_SITE = https://github.com/Ryubing/Stable-Releases/releases/download/$(RYUJINX_VERSION)
RYUJINX_LICENSE = MIT
RYUJINX_DEPENDENCIES = sdl2 openal hicolor-icon-theme adwaita-icon-theme librsvg

ifeq ($(BR2_x86_64),y)
RYUJINX_SOURCE = ryujinx-$(RYUJINX_VERSION)-linux_x64.tar.gz
else ifeq ($(BR2_aarch64),y)
RYUJINX_SOURCE = ryujinx-$(RYUJINX_VERSION)-linux_arm64.tar.gz
endif

define RYUJINX_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && \
	    tar xf $(DL_DIR)/$(RYUJINX_DL_SUBDIR)/$(RYUJINX_SOURCE)
endef

define RYUJINX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/ryujinx
	cp -pr $(@D)/target/publish/* $(TARGET_DIR)/usr/ryujinx
endef

$(eval $(generic-package))
