################################################################################
#
# LEDSpicer
#
################################################################################

LEDSPICER_VERSION = 7e8957edebe9fd6e209ac824dfe109edb3de36d9
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

# Stage files in an 'init' directory to be used by the LEDSpicer service
# Default contents of /usr/share/ledspicer (except 'doc') move to '/usr/share/ledspicer/init'
define LEDSPICER_SERVICE_INIT
    mkdir -p $(TARGET_DIR)/usr/share/ledspicer/init
    for f in $(TARGET_DIR)/usr/share/ledspicer/*; do \
        test "$$f" == "$(TARGET_DIR)/usr/share/ledspicer/doc" && continue; \
        test "$$f" == "$(TARGET_DIR)/usr/share/ledspicer/init" && continue; \
        mv "$$f" "$(TARGET_DIR)/usr/share/ledspicer/init/"; \
    done
endef

define LEDSPICER_SERVICE_INSTALL
    mkdir -p $(TARGET_DIR)/usr/share/batocera/services
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/ledspicer/ledspicer $(TARGET_DIR)/usr/share/batocera/services/
endef

LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_SERVICE_INIT
LEDSPICER_POST_INSTALL_TARGET_HOOKS += LEDSPICER_SERVICE_INSTALL

$(eval $(autotools-package))