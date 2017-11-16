################################################################################
#
# FSUAE_CAPSIMG_PLUGIN
#
################################################################################

FSUAE_CAPSIMG_PLUGIN_VERSION = 067db4cc6bfdcd1ab684b812da6fedbb8f96e04a
FSUAE_CAPSIMG_PLUGIN_SITE = $(call github,FrodeSolheim,capsimg,$(FSUAE_CAPSIMG_PLUGIN_VERSION))

define FSUAE_CAPSIMG_PLUGIN_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_CAPSIMG_PLUGIN_PRE_CONFIGURE_HOOKS += FSUAE_CAPSIMG_PLUGIN_HOOK_BOOTSTRAP

define FSUAE_CAPSIMG_PLUGIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/capsimg.so \
		$(TARGET_DIR)/usr/share/FS-UAE/Plugins/capsimg.so
        echo "$(FSUAE_CAPSIMG_PLUGIN_VERSION)" > $(TARGET_DIR)/usr/share/FS-UAE/Plugins/Version.txt
endef

$(eval $(autotools-package))
