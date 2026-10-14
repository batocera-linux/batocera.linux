################################################################################
#
# meson-firmware
#
################################################################################

MESON_FIRMWARE_VERSION = 662b843714ac18e92b19887fadc8d8b3d94fc814
MESON_FIRMWARE_SITE = $(call github,LibreELEC,meson-firmware,$(MESON_FIRMWARE_VERSION))
MESON_FIRMWARE_LICENSE = Proprietary
MESON_FIRMWARE_LICENSE_FILES = LICENSE

define MESON_FIRMWARE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/meson/vdec $(TARGET_DIR)/lib/optee_armtz
	cp $(@D)/meson/vdec/* $(TARGET_DIR)/lib/firmware/meson/vdec/
	cp $(@D)/optee_armtz/*.ta $(TARGET_DIR)/lib/optee_armtz/
endef

$(eval $(generic-package))
