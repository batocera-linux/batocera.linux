################################################################################
#
# BATOCERA AUDIO
#
################################################################################

BATOCERA_AUDIO_VERSION = 5
BATOCERA_AUDIO_LICENSE = GPL
BATOCERA_AUDIO_DEPENDENCIES = alsa-lib
BATOCERA_AUDIO_SOURCE=
BATOCERA_AUDIO_DEPENDENCIES += alsa-plugins

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
ALSA_SUFFIX = "-odroidga"
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
ALSA_SUFFIX = "-rk3399"
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
ALSA_SUFFIX = "-s922x"
else
ALSA_SUFFIX = 
endif

define BATOCERA_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/python3.9 \
		$(TARGET_DIR)/usr/bin \
		$(TARGET_DIR)/usr/share/sounds \
		$(TARGET_DIR)/usr/share/batocera/alsa \
		$(TARGET_DIR)/etc/init.d \
		$(TARGET_DIR)/etc/udev/rules.d
	# default alsa configurations
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/asoundrc-* \
		$(TARGET_DIR)/usr/share/batocera/alsa/
	# sample audio files
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/*.wav $(TARGET_DIR)/usr/share/sounds
	# init script
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/S01audio \
		$(TARGET_DIR)/etc/init.d/S01audio
	# udev script to unmute audio devices
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/90-alsa-setup.rules \
		$(TARGET_DIR)/etc/udev/rules.d/90-alsa-setup.rules
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/soundconfig \
		$(TARGET_DIR)/usr/bin/soundconfig
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/batocera-audio$(ALSA_SUFFIX) \
		$(TARGET_DIR)/usr/bin/batocera-audio
endef

$(eval $(generic-package))
