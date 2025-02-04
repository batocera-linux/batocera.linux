################################################################################
#
# rmtfs
#
################################################################################

RMTFS_VERSION = 33e1e40615efc59b17a515afe857c51b8b8c1ad1
RMTFS_SITE = $(call github,andersson,rmtfs,$(RMTFS_VERSION))
RMTFS_LICENSE = BSD-3-Clause license
RMTFS_LICENSE_FILE = LICENSE
RMTFS_DEPENDENCIES = host-qrtr qrtr eudev
RMTFS_INSTALL_STAGING = YES

define RMTFS_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS)  \
        CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr -ludev -lpthread" -C $(@D) 
endef

define RMTFS_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/rmtfs $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
