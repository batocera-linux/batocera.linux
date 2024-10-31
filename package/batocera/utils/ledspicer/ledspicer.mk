################################################################################
#
# ledspicer
#
################################################################################

LEDSPICER_VERSION = 0.6.3.1
LEDSPICER_SITE = $(call github,meduzapat,LEDSpicer,$(LEDSPICER_VERSION))
LEDSPICER_LICENSE = GPLv3
LEDSPICER_DEPENDENCIES = tinyxml2 libusb libtool udev libpthread-stubs
LEDSPICER_AUTORECONF = YES
LEDSPICER_CONF_OPTS = CXXFLAGS='-g0 -O3' --enable-nanoled --enable-pacdrive --enable-pacled64
LEDSPICER_CONF_OPTS += --enable-ultimateio --enable-ledwiz32 --enable-howler --enable-adalight
LEDSPICER_CONF_OPTS += --sysconfdir=/userdata/system/configs/ledspicer
LEDSPICER_CONF_OPTS += --docdir=/usr/share/ledspicer/doc

ifeq ($(BR2_PACKAGE_PIGPIO),y)
    LEDSPICER_DEPENDENCIES += pigpio
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
    LEDSPICER_CONF_OPTS += --enable-pulseaudio
    LEDSPICER_DEPENDENCIES += pulseaudio
else
    LEDSPICER_CONF_OPTS += --disable-pulseaudio
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
    LEDSPICER_CONF_OPTS += --enable-alsaaudio
    LEDSPICER_DEPENDENCIES += alsa-lib
else
    LEDSPICER_CONF_OPTS += --disable-alsaaudio
endif

ifeq ($(BR2_PACKAGE_BATOCERA_RPI_ANY),y)
	LEDSPICER_CONF_OPTS += --enable-raspberrypi
else
	LEDSPICER_CONF_OPTS += --disable-raspberrypi
endif

define LEDSPICER_UDEV_RULE
    mkdir -p $(TARGET_DIR)/etc/udev/rules.d
    cp $(@D)/data/21-ledspicer.rules $(TARGET_DIR)/etc/udev/rules.d/99-ledspicer.rules
endef

define LEDSPICER_SERVICE_INSTALL
    mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/ledspicer/ledspicer \
        $(TARGET_DIR)/usr/share/batocera/services/
endef

LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_UDEV_RULE
LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_SERVICE_INSTALL

$(eval $(autotools-package))
