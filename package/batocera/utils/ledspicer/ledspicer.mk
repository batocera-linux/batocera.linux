################################################################################
#
# LEDSpicer
#
################################################################################

LEDSPICER_VERSION = 4add69ba78068a48066f3c5e8ebe72f0ef2e27ad
LEDSPICER_SITE = $(call github,meduzapat,LEDSpicer,$(LEDSPICER_VERSION))
LEDSPICER_LICENSE = GPLv3
LEDSPICER_DEPENDENCIES = tinyxml2 libusb libtool udev
LEDSPICER_AUTORECONF = YES
LEDSPICER_CONF_OPTS = CXXFLAGS='-g0 -O3' --enable-nanoled --enable-pacdrive --enable-pacled64 --enable-ultimateio --enable-ledwiz32 --enable-howler --enable-adalight

# Move doc from /usr/share/doc/ledspicer to /usr/share/ledspicer/doc to conform to Batocera
LEDSPICER_CONF_OPTS += --docdir=/usr/share/ledspicer/doc

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

define LEDSPICER_APPLY_UDEV_RULES
	cp $(@D)/data/21-ledspicer.rules $(TARGET_DIR)/etc/udev/rules.d/99-ledspicer.rules
endef

define LEDSPICER_ENABLE_SERVICE
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/ledspicer/ledspicer.service $(TARGET_DIR)/etc/init.d/S90ledspicer
endef

define LEDSPICER_EXTERNALIZE_CONFIG
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer

    cp $(TARGET_DIR)/usr/share/ledspicer/doc/examples/ledspicer.conf $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/ledspicer.conf
    ln -sf /userdata/system/configs/ledspicer/ledspicer.conf $(TARGET_DIR)/etc/ledspicer.conf

    mv $(TARGET_DIR)/usr/share/ledspicer/basicColors.xml $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/basicColors.xml
    ln -sf /userdata/system/configs/ledspicer/basicColors.xml $(TARGET_DIR)/usr/share/ledspicer/basicColors.xml

    mv $(TARGET_DIR)/usr/share/ledspicer/gameData.xml $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/gameData.xml
    ln -sf /userdata/system/configs/ledspicer/gameData.xml $(TARGET_DIR)/usr/share/ledspicer/gameData.xml

    mv $(TARGET_DIR)/usr/share/ledspicer/animations $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/animations
    ln -sf /userdata/system/configs/ledspicer/animations $(TARGET_DIR)/usr/share/ledspicer/animations

    mv $(TARGET_DIR)/usr/share/ledspicer/inputs $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/inputs
    ln -sf /userdata/system/configs/ledspicer/inputs $(TARGET_DIR)/usr/share/ledspicer/inputs

    mv $(TARGET_DIR)/usr/share/ledspicer/profiles $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/profiles
    ln -sf /userdata/system/configs/ledspicer/profiles $(TARGET_DIR)/usr/share/ledspicer/profiles

    mv $(TARGET_DIR)/usr/share/ledspicer/umaps $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/ledspicer/umaps
    ln -sf /userdata/system/configs/ledspicer/umaps $(TARGET_DIR)/usr/share/ledspicer/umaps

endef

LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_APPLY_UDEV_RULES
LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_ENABLE_SERVICE
LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_EXTERNALIZE_CONFIG

$(eval $(autotools-package))