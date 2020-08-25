################################################################################
#
# BATOCERA AUDIO
#
################################################################################

BATOCERA_AUDIO_VERSION = 4.1
BATOCERA_AUDIO_LICENSE = GPL
BATOCERA_AUDIO_DEPENDENCIES = alsa-lib
BATOCERA_AUDIO_SOURCE=
BATOCERA_AUDIO_DEPENDENCIES += pulseaudio alsa-plugins

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI_ANY),y)
ALSA_SUFFIX = "-rpi"
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
ALSA_SUFFIX = "-odroidga"
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
ALSA_SUFFIX = "-rockpro64"
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
ALSA_SUFFIX = "-vim3"
else
ALSA_SUFFIX = 
endif

define BATOCERA_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/python2.7 $(TARGET_DIR)/usr/bin $(TARGET_DIR)/usr/share/sounds $(TARGET_DIR)/usr/share/batocera/alsa
	# default alsa configurations
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/asoundrc-* \
		$(TARGET_DIR)/usr/share/batocera/alsa/
	# sample audio files
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/*.wav $(TARGET_DIR)/usr/share/sounds
	# init script
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/S15audio \
		$(TARGET_DIR)/etc/init.d/S15audio
	# udev script to unmute audio devices
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/90-alsa-setup.rules \
		$(TARGET_DIR)/etc/udev/rules.d/90-alsa-setup.rules
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/soundconfig \
		$(TARGET_DIR)/usr/bin/soundconfig
	# pulseaudio: conf files
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/client.conf \
		$(TARGET_DIR)/etc/pulse/client.conf
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/default.pa  \
		$(TARGET_DIR)/etc/pulse/default.pa
	# pulseaudio: batocera-audio
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/batocera-audio \
		$(TARGET_DIR)/usr/bin/batocera-audio-pulseaudio
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/batocera-audio$(ALSA_SUFFIX) \
		$(TARGET_DIR)/usr/bin/batocera-audio-alsa
endef

$(eval $(generic-package))
