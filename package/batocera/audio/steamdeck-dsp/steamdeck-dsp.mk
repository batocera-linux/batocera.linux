################################################################################
#
# steamdeck-dsp
#
################################################################################

STEAMDECK_DSP_VERSION = 0.83-1
STEAMDECK_DSP_SOURCE =
STEAMDECK_DSP_LICENSE = LGPL-2.1+

STEAMDECK_DSP_DEPENDENCIES = pipewire wireplumber

STEAMDECK_DSP_FILES = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/audio/steamdeck-dsp

define STEAMDECK_DSP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr
	mkdir -p $(TARGET_DIR)/lib
	rsync -a $(STEAMDECK_DSP_FILES)/usr $(TARGET_DIR)/
	rsync -a $(STEAMDECK_DSP_FILES)/lib $(TARGET_DIR)/
endef

$(eval $(generic-package))
