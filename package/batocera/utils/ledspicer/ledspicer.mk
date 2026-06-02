################################################################################
#
# ledspicer
#
################################################################################

LEDSPICER_VERSION = 0.7.4.1
LEDSPICER_SITE = $(call github,meduzapat,LEDSpicer,$(LEDSPICER_VERSION))
LEDSPICER_LICENSE = GPLv3
LEDSPICER_DEPENDENCIES = tinyxml2 libusb libtool udev libpthread-stubs
LEDSPICER_AUTORECONF = YES
LEDSPICER_CONF_OPTS = -DENABLE_NANOLED=ON -DENABLE_PACDRIVE=ON -DENABLE_PACLED64=ON
LEDSPICER_CONF_OPTS += -DENABLE_ULTIMATEIO=ON -DENABLE_LEDWIZ32=ON -DENABLE_HOWLER=ON -DENABLE_ADALIGHT=ON
LEDSPICER_CONF_OPTS += -DINSTALL_FULL_DATADIR=/userdata/system/configs/
LEDSPICER_CONF_OPTS += -DINSTALL_SYSCONFDIR=/userdata/system/configs/ledspicer
LEDSPICER_CONF_OPTS += -DINSTALL_DOCDIR=/usr/share/ledspicer/doc

ifeq ($(BR2_PACKAGE_PIGPIO),y)
    LEDSPICER_DEPENDENCIES += pigpio
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
    LEDSPICER_CONF_OPTS += -DENABLE_PULSEAUDIO=ON
    LEDSPICER_DEPENDENCIES += pulseaudio
else
    LEDSPICER_CONF_OPTS += -DENABLE_PULSAUDIO=OFF
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
    LEDSPICER_CONF_OPTS += -DENABLE_ALSAUDIO=ON
    LEDSPICER_DEPENDENCIES += alsa-lib
else
    LEDSPICER_CONF_OPTS += -DENABLE_ALSAUDIO=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_RPI_ANY),y)
	LEDSPICER_CONF_OPTS += -DENABLE_RASPERRYPI=ON
else
	LEDSPICER_CONF_OPTS += -DENABLE_RASPERRYPI=OFF
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

$(eval $(cmake-package))
