################################################################################
#
# BATOCERA AUDIO
#
################################################################################

BATOCERA_AUDIO_VERSION = 2.2
BATOCERA_AUDIO_LICENSE = GPL
BATOCERA_AUDIO_DEPENDENCIES = alsa-lib
BATOCERA_AUDIO_SOURCE=
BATOCERA_AUDIO_DEPENDENCIES += pulseaudio alsa-plugins
BATOCERA_AUDIO_POST_INSTALL_TARGET_HOOKS += BATOCERA_AUDIO_INSTALL_PULSEAUDIO_CONF

define BATOCERA_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/python2.7 $(TARGET_DIR)/usr/bin $(TARGET_DIR)/usr/share/sounds
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/Mallet.wav $(TARGET_DIR)/usr/share/sounds
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/batocera-audio $(TARGET_DIR)/usr/bin/batocera-audio
endef

define BATOCERA_AUDIO_INSTALL_PULSEAUDIO_CONF
	# init script
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/S15audio               $(TARGET_DIR)/etc/init.d/S15audio
	# override  conf files
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/client.conf $(TARGET_DIR)/etc/pulse/client.conf
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/default.pa  $(TARGET_DIR)/etc/pulse/default.pa
	# udev script to unmute audio devices
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/90-alsa-setup.rules    $(TARGET_DIR)/etc/udev/rules.d/90-alsa-setup.rules
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/soundconfig            $(TARGET_DIR)/usr/bin/soundconfig
endef

$(eval $(generic-package))
