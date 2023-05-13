################################################################################
#
# sound-open-firmware
#
################################################################################

SOUND_OPEN_FIRMWARE_VERSION = v2.2.5
SOUND_OPEN_FIRMWARE_SOURCE = sof-bin-$(SOUND_OPEN_FIRMWARE_VERSION).tar.gz
SOUND_OPEN_FIRMWARE_SITE = https://github.com/thesofproject/sof-bin/releases/download/$(SOUND_OPEN_FIRMWARE_VERSION)
SOUND_OPEN_FIRMWARE_LICENSE = BSD-3-Clause
SOUND_OPEN_FIRMWARE_LICENSE_FILES = LICENSE

SOUND_OPEN_FIRMWARE_DEPENDENCIES = alsa-lib alsa-utils alllinuxfirmwares

define SOUND_OPEN_FIRMWARE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/lib/firmware/intel
	rsync -arv $(@D)/sof-$(SOUND_OPEN_FIRMWARE_VERSION) $(TARGET_DIR)/lib/firmware/intel/
	rsync -arv $(@D)/sof-tplg-$(SOUND_OPEN_FIRMWARE_VERSION) $(TARGET_DIR)/lib/firmware/intel/
	# symbolic links
	ln -srf "$(TARGET_DIR)/lib/firmware/intel"/{sof-$(SOUND_OPEN_FIRMWARE_VERSION),sof}
	ln -srf "$(TARGET_DIR)/lib/firmware/intel"/{sof-tplg-$(SOUND_OPEN_FIRMWARE_VERSION),sof-tplg}
endef

$(eval $(generic-package))
