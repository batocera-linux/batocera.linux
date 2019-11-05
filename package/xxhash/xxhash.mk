################################################################################
#
# xxhash
#
################################################################################

XXHASH_VERSION = 0.7.1
XXHASH_SITE = $(call github,Cyan4973,xxHash,v$(XXHASH_VERSION))
XXHASH_LICENSE = BSD-2-Clause, GPL-2.0+
XXHASH_LICENSE_FILES = LICENSE xxhsum.c

define XXHASH_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) xxhsum
endef

define XXHASH_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/xxhsum $(TARGET_DIR)/usr/bin/xxhsum
endef

$(eval $(generic-package))
