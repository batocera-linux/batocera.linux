################################################################################
#
# tqftpserv
#
################################################################################

TQFTPSERV_VERSION = 783425b550de2a359db6aa3b41577c3fbaae5903
TQFTPSERV_SITE = $(call github,andersson,tqftpserv,$(TQFTPSERV_VERSION))
TQFTPSERV_LICENSE = BSD-3-Clause license
TQFTPSERV_LICENSE_FILE = LICENSE
TQFTPSERV_DEPENDENCIES = host-qrtr qrtr

define TQFTPSERV_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr" -C $(@D) 
endef

define TQFTPSERV_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/tqftpserv $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
