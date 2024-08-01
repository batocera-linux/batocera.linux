################################################################################
#
# moonlight-embedded
#
################################################################################

MOONLIGHT_EMBEDDED_VERSION = 274d3db34da764344a7a402ee74e6080350ac0cd
MOONLIGHT_EMBEDDED_SITE = https://github.com/moonlight-stream/moonlight-embedded.git
MOONLIGHT_EMBEDDED_SITE_METHOD = git
MOONLIGHT_EMBEDDED_GIT_SUBMODULES=y
MOONLIGHT_EMBEDDED_LICENSE = GPLv3
MOONLIGHT_EMBEDDED_DEPENDENCIES = opus expat libevdev avahi alsa-lib udev \
                                  libcurl libcec ffmpeg sdl2 libenet

MOONLIGHT_EMBEDDED_CONF_OPTS = "-DCMAKE_INSTALL_SYSCONFDIR=/etc"

ifeq ($(BR2_PACKAGE_XORG7),y)
    MOONLIGHT_EMBEDDED_CONF_OPTS += -DENABLE_X11=ON
else
    MOONLIGHT_EMBEDDED_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_LIBVA),y)
    MOONLIGHT_EMBEDDED_DEPENDENCIES += libva-intel-driver intel-mediadriver
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
    MOONLIGHT_EMBEDDED_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_ROCKCHIP_RGA),y)
    MOONLIGHT_EMBEDDED_DEPENDENCIES += rockchip-mpp rockchip-rga
endif

define MOONLIGHT_EMBEDDED_INSTALL_SCRIPTS
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    mkdir -p $(TARGET_DIR)/usr/share/moonlight-embedded
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/moonlight-embedded/moonlight.moonlight.keys \
        $(TARGET_DIR)/usr/share/evmapy
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/moonlight-embedded/moonlight.conf \
        $(TARGET_DIR)/usr/share/moonlight-embedded/
    install -m 0755 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/moonlight-embedded/batocera-moonlight \
	    $(TARGET_DIR)/usr/bin/
endef

MOONLIGHT_EMBEDDED_POST_INSTALL_TARGET_HOOKS += MOONLIGHT_EMBEDDED_INSTALL_SCRIPTS

$(eval $(cmake-package))
