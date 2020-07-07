################################################################################
#
# drminfo
#
################################################################################
# Version.: Commits on May 27, 2020
BATOCERA_DRMINFO_VERSION = 1
BATOCERA_DRMINFO_SOURCE =
BATOCERA_DRMINFO_LICENSE = GPLv3+
BATOCERA_DRMINFO_DEPENDENCIES = libdrm

define BATOCERA_DRMINFO_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(TARGET_CC) -I$(STAGING_DIR)/usr/include/drm -ldrm $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-drminfo/batocera-drminfo.c -o $(@D)/batocera-drminfo
endef

define BATOCERA_DRMINFO_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/batocera-drminfo $(TARGET_DIR)/usr/bin/batocera-drminfo
endef

$(eval $(generic-package))
