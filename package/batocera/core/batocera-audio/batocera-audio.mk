################################################################################
#
# BATOCERA AUDIO
#
################################################################################

BATOCERA_AUDIO_VERSION = 6.2
BATOCERA_AUDIO_LICENSE = GPL
BATOCERA_AUDIO_SOURCE=

# this one is important because the package erase the default pipewire config files, so it must be built after it
BATOCERA_AUDIO_DEPENDENCIES = pipewire

define BATOCERA_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR) \
		$(TARGET_DIR)/usr/bin \
		$(TARGET_DIR)/usr/share/sounds \
		$(TARGET_DIR)/usr/share/batocera/alsa \
		$(TARGET_DIR)/etc/init.d \
		$(TARGET_DIR)/etc/udev/rules.d \
		$(TARGET_DIR)/etc/dbus-1/system.d \
		$(TARGET_DIR)/etc/alsa/conf.d \
		$(TARGET_DIR)/usr/share/pipewire/media-session.d

	# default alsa configurations
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/asoundrc-* \
		$(TARGET_DIR)/usr/share/batocera/alsa/
	# sample audio files
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/*.wav $(TARGET_DIR)/usr/share/sounds

	# extra ucm files
	mkdir -p $(TARGET_DIR)/usr/share/alsa/ucm2
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/ucm2/* $(TARGET_DIR)/usr/share/alsa/ucm2/

	# init script
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/Saudio \
		$(TARGET_DIR)/etc/init.d/S06audio
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/S27audioconfig \
		$(TARGET_DIR)/etc/init.d/S27audioconfig
	# udev script to unmute audio devices
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/90-alsa-setup.rules \
		$(TARGET_DIR)/etc/udev/rules.d/90-alsa-setup.rules
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/soundconfig \
		$(TARGET_DIR)/usr/bin/soundconfig
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/batocera-audio \
		$(TARGET_DIR)/usr/bin/batocera-audio
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/batocera-mixer \
		$(TARGET_DIR)/usr/bin/batocera-mixer

	# pipewire-pulse policy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio-system.conf \
		$(TARGET_DIR)/etc/dbus-1/system.d

	# pipewire-alsa
	ln -sft $(TARGET_DIR)/etc/alsa/conf.d \
		/usr/share/alsa/alsa.conf.d/{50-pipewire,99-pipewire-default}.conf

	# pipewire-media-session config: disable dbus device reservation
    mkdir -p $(TARGET_DIR)/usr/share/wireplumber/main.lua.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/50-alsa-config.lua \
		$(TARGET_DIR)/usr/share/wireplumber/main.lua.d/50-alsa-config.lua

	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pipewire.conf \
		$(TARGET_DIR)/usr/share/pipewire/pipewire.conf
endef

$(eval $(generic-package))
