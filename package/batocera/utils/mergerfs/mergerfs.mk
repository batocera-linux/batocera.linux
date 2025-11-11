################################################################################
#
#  mergerfs
#
#################################################################################
MERGERFS_VERSION = 2.40.2
MERGERFS_SOURCE = mergerfs-$(MERGERFS_VERSION).tar.gz
MERGERFS_SITE = $(call github,trapexit,mergerfs,$(MERGERFS_VERSION))
MERGERFS_LICENSE = MIT
MERGERFS_DEPENDENCIES = host-pkgconf
MERGERFS_LDFLAGS = $(TARGET_LDFLAGS)
MERGERFS_CXXFLAGS = $(TARGET_CXXFLAGS) -O2 -fno-plt -fPIC
ifeq ($(BR2_STATIC_LIBS),y)
MERGERFS_LDFLAGS += -static
endif
MERGERFS_TARGET = mergerfs

define MERGERFS_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
		AR="$(TARGET_AR)" LD="$(TARGET_LD)" \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		CXXFLAGS="$(MERGERFS_CXXFLAGS)" \
		LDFLAGS="$(MERGERFS_LDFLAGS)" \
		$(MERGERFS_TARGET)
endef

define MERGERFS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/build/$(MERGERFS_TARGET) $(TARGET_DIR)/usr/bin/mergerfs
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/mergerfs/S12mergerfs $(TARGET_DIR)/etc/init.d/
endef

$(eval $(generic-package))

