################################################################################
#
# redream
#
################################################################################

REDREAM_VERSION = 1.5.0-1133-g03c2ae9
REDREAM_SITE = https://redream.io/download

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
REDREAM_SOURCE = redream.universal-raspberry-linux-v$(REDREAM_VERSION).tar.gz
else
REDREAM_SOURCE = redream.x86_64-linux-v$(REDREAM_VERSION).tar.gz
endif

define REDREAM_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && \
	    tar xf $(DL_DIR)/$(REDREAM_DL_SUBDIR)/$(REDREAM_SOURCE)
endef

define REDREAM_RPI4_RENAME_ELF
    mv $(@D)/target/redream.aarch64.elf $(@D)/target/redream
endef

define REDREAM_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/target/redream $(TARGET_DIR)/usr/bin/redream
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/redream/dreamcast.redream.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    REDREAM_PRE_INSTALL_TARGET_HOOKS += REDREAM_RPI4_RENAME_ELF
endif

$(eval $(generic-package))
