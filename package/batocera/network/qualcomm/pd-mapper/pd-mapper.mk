################################################################################
#
# pd-mapper
#
################################################################################

PD_MAPPER_VERSION = 9d78fc0c6143c4d1b7198c57be72a6699ce764c4
PD_MAPPER_SITE = $(call github,andersson,pd-mapper,$(PD_MAPPER_VERSION))
PD_MAPPER_LICENSE_FILE = LICENSE
PD_MAPPER_DEPENDENCIES = host-qrtr qrtr

define PD_MAPPER_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr" -C $(@D) 
endef

define PD_MAPPER_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/pd-mapper $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
