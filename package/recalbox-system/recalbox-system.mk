################################################################################
#
# Recalbox System
#
################################################################################

RECALBOX_SYSTEM_SOURCE=

RECALBOX_SYSTEM_VERSION=0.1

ifeq ($(BR2_cortex_a7),y)
	RECALBOX_SYSTEM_RPI_VERSION = rpi2
else
	RECALBOX_SYSTEM_RPI_VERSION = rpi1
endif

define RECALBOX_SYSTEM_INSTALL_TARGET_CMDS
	echo -n "$(RECALBOX_SYSTEM_RPI_VERSION)" > $(TARGET_DIR)/recalbox/recalbox.arch
endef

$(eval $(generic-package))
