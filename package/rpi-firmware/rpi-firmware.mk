################################################################################
#
# rpi-firmware
#
################################################################################

RPI_FIRMWARE_VERSION = dc3afd4c8b885e75f624efb266d65fc00a8a4219
RPI_FIRMWARE_SITE = $(call github,raspberrypi,firmware,$(RPI_FIRMWARE_VERSION))
RPI_FIRMWARE_LICENSE = BSD-3c
RPI_FIRMWARE_LICENSE_FILES = boot/LICENCE.broadcom
RPI_FIRMWARE_INSTALL_TARGET = NO
RPI_FIRMWARE_INSTALL_IMAGES = YES

define RPI_FIRMWARE_INSTALL_IMAGES_CMDS
	for ovldtb in  $(@D)/boot/overlays/*.dtb; do \
		$(INSTALL) -D -m 0644 $${ovldtb} $(BINARIES_DIR)/rpi-firmware/overlays/$${ovldtb##*/} || exit 1; \
	done
	$(INSTALL) -D -m 0644 $(@D)/boot/bootcode.bin $(BINARIES_DIR)/rpi-firmware/bootcode.bin
	$(INSTALL) -D -m 0644 $(@D)/boot/start$(BR2_PACKAGE_RPI_FIRMWARE_BOOT).elf $(BINARIES_DIR)/rpi-firmware/start.elf
	$(INSTALL) -D -m 0644 $(@D)/boot/fixup$(BR2_PACKAGE_RPI_FIRMWARE_BOOT).dat $(BINARIES_DIR)/rpi-firmware/fixup.dat
	$(INSTALL) -D -m 0644 package/rpi-firmware/config.txt $(BINARIES_DIR)/rpi-firmware/config.txt
	$(INSTALL) -D -m 0644 package/rpi-firmware/cmdline.txt $(BINARIES_DIR)/rpi-firmware/cmdline.txt
endef

ifeq ($(BR2_cortex_a7),y)
	RPI_FIRMWARE_INSTALL_IMAGES_CMDS += ; $(INSTALL) -D -m 0644 $(@D)/boot/bcm2709-rpi-2-b.dtb $(BINARIES_DIR)/rpi-firmware/bcm2709-rpi-2-b.dtb
else
 	RPI_FIRMWARE_INSTALL_IMAGES_CMDS += ; $(INSTALL) -D -m 0644 $(@D)/boot/bcm2708-rpi-b.dtb $(BINARIES_DIR)/rpi-firmware/bcm2708-rpi-b.dtb
        RPI_FIRMWARE_INSTALL_IMAGES_CMDS += ; $(INSTALL) -D -m 0644 $(@D)/boot/bcm2708-rpi-b-plus.dtb $(BINARIES_DIR)/rpi-firmware/bcm2708-rpi-b-plus.dtb        
endif


# We have no host sources to get, since we already
# bundle the script we want to install.
HOST_RPI_FIRMWARE_SOURCE =
HOST_RPI_FIRMWARE_DEPENDENCIES =

define HOST_RPI_FIRMWARE_INSTALL_CMDS
	$(INSTALL) -D -m 0755 package/rpi-firmware/mkknlimg $(HOST_DIR)/usr/bin/mkknlimg
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
