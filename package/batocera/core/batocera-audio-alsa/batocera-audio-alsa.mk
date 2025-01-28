################################################################################
#
# BATOCERA AUDIO ALSA
#
################################################################################

BATOCERA_AUDIO_ALSA_VERSION = 1.0
BATOCERA_AUDIO_ALSA_LICENSE = GPL
BATOCERA_AUDIO_ALSA_DEPENDENCIES = alsa-lib
BATOCERA_AUDIO_ALSA_SOURCE=
BATOCERA_AUDIO_ALSA_DEPENDENCIES += alsa-plugins

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI_ANY),y)
ALSA_SUFFIX = "-bcm"
else
ALSA_SUFFIX =
endif

define BATOCERA_AUDIO_ALSA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin $(TARGET_DIR)/usr/share/sounds $(TARGET_DIR)/usr/share/batocera/alsa $(TARGET_DIR)/etc/init.d $(TARGET_DIR)/etc/udev/rules.d
	# default alsa configurations
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio-alsa/alsa/asoundrc-* \
		$(TARGET_DIR)/usr/share/batocera/alsa/
	# sample audio files
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio-alsa/*.wav $(TARGET_DIR)/usr/share/sounds
	# init script
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio-alsa/S01audio \
		$(TARGET_DIR)/etc/init.d/S01audio
	# udev script to unmute audio devices
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio-alsa/90-alsa-setup.rules \
		$(TARGET_DIR)/etc/udev/rules.d/90-alsa-setup.rules
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio-alsa/soundconfig \
		$(TARGET_DIR)/usr/bin/soundconfig
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio-alsa/alsa/batocera-audio$(ALSA_SUFFIX) \
		$(TARGET_DIR)/usr/bin/batocera-audio
endef

$(eval $(generic-package))
