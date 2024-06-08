################################################################################
#
# nv-codec-headers
#
################################################################################
# align to nvidia production driver - 550.54.14 or greater
NV_CODEC_HEADERS_VERSION = n12.2.72.0
NV_CODEC_HEADERS_SITE = https://github.com/FFmpeg/nv-codec-headers
NV_CODEC_HEADERS_SITE_METHOD = git
NV_CODEC_HEADERS_INSTALL_STAGING = YES

define NV_CODEC_HEADERS_INSTALL_STAGING_CMDS
	$(MAKE) PREFIX=$(STAGING_DIR)/usr -C $(@D) install
endef

define NV_CODEC_HEADERS_INSTALL_TARGET_CMDS
	$(MAKE) PREFIX=$(TARGET_DIR)/usr -C $(@D) install
endef

$(eval $(generic-package))
