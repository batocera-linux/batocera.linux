################################################################################
#
# Recalbox System
#
################################################################################

RECALBOX_SYSTEM_SOURCE=

RECALBOX_SYSTEM_VERSION=0.2

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
	RECALBOX_SYSTEM_VERSION=rpi3
	RECALBOX_SYSTEM_RECALBOX_CONF=rpi3
	RECALBOX_SYSTEM_SUBDIR=rpi-firmware
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_XU4),y)
	RECALBOX_SYSTEM_VERSION=xu4
	RECALBOX_SYSTEM_RECALBOX_CONF=xu4
	RECALBOX_SYSTEM_SUBDIR=
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_X86),y)
	RECALBOX_SYSTEM_VERSION=x86
	RECALBOX_SYSTEM_RECALBOX_CONF=x86
	RECALBOX_SYSTEM_SUBDIR=
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_X86_64),y)
	RECALBOX_SYSTEM_VERSION=x86_64
	RECALBOX_SYSTEM_RECALBOX_CONF=x86_64
	RECALBOX_SYSTEM_SUBDIR=
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
	RECALBOX_SYSTEM_VERSION=rpi2
	RECALBOX_SYSTEM_RECALBOX_CONF=rpi2
	RECALBOX_SYSTEM_SUBDIR=rpi-firmware
else
	RECALBOX_SYSTEM_VERSION=rpi1
	RECALBOX_SYSTEM_RECALBOX_CONF=rpi1
	RECALBOX_SYSTEM_SUBDIR=rpi-firmware
endif

define RECALBOX_SYSTEM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/recalbox/
	echo -n "$(RECALBOX_SYSTEM_VERSION)" > $(TARGET_DIR)/recalbox/recalbox.arch
	mkdir -p $(TARGET_DIR)/recalbox/share_init/system
	cp package/recalbox-system/$(RECALBOX_SYSTEM_RECALBOX_CONF)/recalbox.conf $(TARGET_DIR)/recalbox/share_init/system
	cp package/recalbox-system/$(RECALBOX_SYSTEM_RECALBOX_CONF)/recalbox.conf $(TARGET_DIR)/recalbox/share_init/system/recalbox.conf.template
	# recalbox-boot.conf
        $(INSTALL) -D -m 0644 package/recalbox-system/recalbox-boot.conf $(BINARIES_DIR)/$(RECALBOX_SYSTEM_SUBDIR)/recalbox-boot.conf
endef

$(eval $(generic-package))
