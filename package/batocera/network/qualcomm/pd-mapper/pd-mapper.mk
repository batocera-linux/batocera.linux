################################################################################
#
# pd-mapper
#
################################################################################

PD_MAPPER_VERSION = v1.1
PD_MAPPER_SITE = $(call github,linux-msm,pd-mapper,$(PD_MAPPER_VERSION))
PD_MAPPER_LICENSE_FILE = LICENSE
PD_MAPPER_DEPENDENCIES = qrtr xz

PD_MAPPER_MAKE_OPTS = \
    prefix=/usr \
    LDFLAGS="$(TARGET_LDFLAGS) -lqrtr -llzma"

define PD_MAPPER_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) \
        $(PD_MAPPER_MAKE_OPTS) -C $(@D)
endef

define PD_MAPPER_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/pd-mapper $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
