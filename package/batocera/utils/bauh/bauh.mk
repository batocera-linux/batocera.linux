################################################################################
#
# bauh
#
################################################################################

BAUH_VERSION = 0.10.7
BAUH_SITE =  $(call github,vinifmor,bauh,$(BAUH_VERSION))
BAUH_SETUP_TYPE = setuptools

define BAUH_KEEP_FLATPAK_ONLY
    rm -rf $(TARGET_DIR)/usr/lib/python*/site-packages/bauh/gems/{snap,web,arch,appimage}
endef

BAUH_POST_INSTALL_TARGET_HOOKS += BAUH_KEEP_FLATPAK_ONLY

$(eval $(python-package))
