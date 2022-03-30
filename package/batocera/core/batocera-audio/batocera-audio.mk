################################################################################
#
# BATOCERA AUDIO
#
################################################################################

BATOCERA_AUDIO_VERSION = 6.1
BATOCERA_AUDIO_LICENSE = GPL
BATOCERA_AUDIO_SOURCE=

# this one is important because the package erase the default pipewire config files, so it must be built after it
BATOCERA_AUDIO_DEPENDENCIES = pipewire

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
ALSA_SUFFIX = "-rk3326"
PIPEWIRECONF_SUFFIX = "-rk3326"
else
ALSA_SUFFIX =
PIPEWIRECONF_SUFFIX =
endif

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
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/batocera-audio$(ALSA_SUFFIX) \
		$(TARGET_DIR)/usr/bin/batocera-audio
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/alsa/batocera-mixer \
		$(TARGET_DIR)/usr/bin/batocera-mixer

	# pipewire-pulse policy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pulseaudio-system.conf \
		$(TARGET_DIR)/etc/dbus-1/system.d

	# pipewire-alsa
	ln -sft $(TARGET_DIR)/etc/alsa/conf.d \
		/usr/share/alsa/alsa.conf.d/{50-pipewire,99-pipewire-default}.conf
	install -Dm644 /dev/null $(TARGET_DIR)/usr/share/pipewire/media-session.d/with-alsa

	# pipewire-media-session config: disable dbus device reservation
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/media-session.conf \
		$(TARGET_DIR)/usr/share/pipewire/media-session.d

	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pipewire.conf$(PIPEWIRECONF_SUFFIX) \
		$(TARGET_DIR)/usr/share/pipewire/pipewire.conf
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/client-rt.conf \
		$(TARGET_DIR)/usr/share/pipewire/client-rt.conf
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/pipewire-pulse.conf \
		$(TARGET_DIR)/usr/share/pipewire/pipewire-pulse.conf
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-audio/media-session.conf \
		$(TARGET_DIR)/usr/share/pipewire/media-session.d/media-session.conf
endef

$(eval $(generic-package))
