################################################################################
#
# Recalbox System
#
################################################################################

RECALBOX_SYSTEM_SOURCE=

RECALBOX_SYSTEM_VERSION=0.2

ifeq ($(BR2_cortex_a8),y)
	RECALBOX_SYSTEM_RPI_VERSION=rpi3
	RECALBOX_SYSTEM_RECALBOX_CONF=rpi3
else ifeq ($(BR2_cortex_a7),y)
	RECALBOX_SYSTEM_RPI_VERSION=rpi2
	RECALBOX_SYSTEM_RECALBOX_CONF=rpi2
else
	RECALBOX_SYSTEM_RPI_VERSION=rpi1
	RECALBOX_SYSTEM_RECALBOX_CONF=rpi1
endif

define RECALBOX_SYSTEM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/recalbox/
	echo -n "$(RECALBOX_SYSTEM_RPI_VERSION)" > $(TARGET_DIR)/recalbox/recalbox.arch
	mkdir -p $(TARGET_DIR)/recalbox/share_init/system
	cp package/recalbox-system/$(RECALBOX_SYSTEM_RECALBOX_CONF)/recalbox.conf $(TARGET_DIR)/recalbox/share_init/system
	cp package/recalbox-system/$(RECALBOX_SYSTEM_RECALBOX_CONF)/recalbox.conf $(TARGET_DIR)/recalbox/share_init/system/recalbox.conf.template
	# recalbox-boot.conf
        $(INSTALL) -D -m 0644 package/recalbox-system/recalbox-boot.conf $(BINARIES_DIR)/rpi-firmware/recalbox-boot.conf

endef

$(eval $(generic-package))
