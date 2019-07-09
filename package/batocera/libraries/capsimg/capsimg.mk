################################################################################
#
# CAPSIMG
#
################################################################################
# Version.: Commits on Dec 8, 2016
CAPSIMG_VERSION = 067db4cc6bfdcd1ab684b812da6fedbb8f96e04a
CAPSIMG_SITE = $(call github,FrodeSolheim,capsimg,$(CAPSIMG_VERSION))
CAPSIMG_LICENSE = Non-commercial

define CAPSIMG_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

CAPSIMG_PRE_CONFIGURE_HOOKS += CAPSIMG_HOOK_BOOTSTRAP

define CAPSIMG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/capsimg.so \
		$(TARGET_DIR)/usr/share/FS-UAE/Plugins/capsimg.so
        echo "$(CAPSIMG_VERSION)" > $(TARGET_DIR)/usr/share/FS-UAE/Plugins/Version.txt
endef

$(eval $(autotools-package))
