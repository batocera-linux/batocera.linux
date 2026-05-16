################################################################################
#
# rmtfs
#
################################################################################
# v1.2 is buggy!
RMTFS_VERSION = v1.1.1
RMTFS_SITE = $(call github,linux-msm,rmtfs,$(RMTFS_VERSION))
RMTFS_LICENSE = BSD-3-Clause license
RMTFS_LICENSE_FILE = LICENSE
RMTFS_DEPENDENCIES = qrtr eudev

RMTFS_MAKE_OPTS = \
    prefix=/usr \
    LDFLAGS="$(TARGET_LDFLAGS) -lqrtr -ludev -lpthread"

define RMTFS_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) \
        $(RMTFS_MAKE_OPTS) -C $(@D)
endef

define RMTFS_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/rmtfs $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
