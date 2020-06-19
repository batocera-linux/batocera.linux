################################################################################
#
# BATOCERA AUDIO
#
################################################################################

BATOCERA_AUDIO_VERSION = 2.0
BATOCERA_AUDIO_LICENSE = GPL
BATOCERA_AUDIO_DEPENDENCIES = alsa-lib
BATOCERA_AUDIO_SOURCE=

# ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_DMIX),y)
# 	BATOCERA_AUDIO_SCRIPT=dmix
# 	BATOCERA_SCRIPTS_POST_INSTALL_TARGET_HOOKS += BATOCERA_SCRIPTS_INSTALL_AUDIO_DMIX
# else ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_RPI),y)
# 	BATOCERA_AUDIO_SCRIPT=rpi
# else ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_ODROIDGOA),y)
# 	BATOCERA_AUDIO_SCRIPT=odroidgoa
# 	BATOCERA_SCRIPTS_POST_INSTALL_TARGET_HOOKS += BATOCERA_SCRIPTS_INSTALL_AUDIO_DMIX
# else ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_VIM3),y)
# 	BATOCERA_AUDIO_SCRIPT=vim3
# else ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_NONE),y)
# 	BATOCERA_AUDIO_SCRIPT=none
# else
# pulseaudio
BATOCERA_AUDIO_DEPENDENCIES += pulseaudio alsa-plugins
BATOCERA_AUDIO_SCRIPT=pulseaudio
BATOCERA_AUDIO_POST_INSTALL_TARGET_HOOKS += BATOCERA_AUDIO_INSTALL_PULSEAUDIO_CONF
# endif

define BATOCERA_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/python2.7 $(TARGET_DIR)/usr/bin $(TARGET_DIR)/usr/share/sounds
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/Mallet.wav $(TARGET_DIR)/usr/share/sounds
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/batocera-audio-$(BATOCERA_AUDIO_SCRIPT) $(TARGET_DIR)/usr/bin/batocera-audio
endef

# define BATOCERA_AUDIO_INSTALL_AUDIO_DMIX
# 	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/alsa/asound.conf.dmix $(TARGET_DIR)/etc/asound.conf
# endef

define BATOCERA_AUDIO_INSTALL_PULSEAUDIO_CONF
	# init script
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/S15audio    $(TARGET_DIR)/etc/init.d/S15audio
	# override  conf files
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/client.conf $(TARGET_DIR)/etc/pulse/client.conf
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio/default.pa  $(TARGET_DIR)/etc/pulse/default.pa
endef

$(eval $(generic-package))
