################################################################################
#
# pd-mapper
#
################################################################################

PD_MAPPER_VERSION = e7c42e1522249593302a5b8920b9e7b42dc3f25e
PD_MAPPER_SITE = $(call github,andersson,pd-mapper,$(PD_MAPPER_VERSION))
PD_MAPPER_LICENSE_FILE = LICENSE
PD_MAPPER_DEPENDENCIES = host-qrtr qrtr xz

define PD_MAPPER_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" \
        LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/usr/lib -lqrtr -llzma" -C $(@D) 
endef

define PD_MAPPER_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/pd-mapper $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
