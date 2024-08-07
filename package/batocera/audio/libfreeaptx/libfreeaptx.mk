################################################################################
#
# libfreeaptx
#
################################################################################
LIBFREEAPTX_VERSION = c176b7de9c2017d0fc1877659cea3bb6c330aafa
LIBFREEAPTX_SITE =  $(call github,iamthehorker,libfreeaptx,$(LIBFREEAPTX_VERSION))
LIBFREEAPTX_LICENSE = GPLv2.1
LIBFREEAPTX_INSTALL_STAGING = YES

define LIBFREEAPTX_INSTALL_STAGING_CMDS
    $(MAKE) PREFIX="$(STAGING_DIR)/usr" $(TARGET_CONFIGURE_OPTS) -C $(@D) install
endef

define LIBFREEAPTX_INSTALL_TARGET_CMDS
    $(MAKE) PREFIX="$(TARGET_DIR)/usr" $(TARGET_CONFIGURE_OPTS) -C $(@D) install
endef

$(eval $(generic-package))
