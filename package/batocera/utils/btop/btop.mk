################################################################################
#
# btop
#
################################################################################

BTOP_VERSION = v1.2.12
BTOP_SITE = $(call github,aristocratos,btop,$(BTOP_VERSION))
BTOP_LICENSE = Apache-2.0
BTOP_EXTRA_ARGS = 

ifeq ($(BR2_arm),y)
    BTOP_EXTRA_ARGS += ARCH=aarch32
else ifeq ($(BR2_aarch64),y)
    BTOP_EXTRA_ARGS += ARCH=aarch64
endif

ifeq ($(BR2_x86_64),y)
    BTOP_EXTRA_ARGS += ARCH=X86_64
endif

define BTOP_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) $(BTOP_EXTRA_ARGS) -C $(@D)
endef

define BTOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/btop
	$(INSTALL) -D $(@D)/bin/btop $(TARGET_DIR)/usr/bin/btop
	cp -prn $(@D)/themes $(TARGET_DIR)/usr/share/btop/
endef

$(eval $(generic-package))
