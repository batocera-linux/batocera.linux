################################################################################
#
# moonlight-embedded
#
################################################################################
# Version.: Commits on Aug 11, 2018
MOONLIGHT_EMBEDDED_VERSION = 2.4.7
MOONLIGHT_EMBEDDED_SOURCE = moonlight-embedded-$(MOONLIGHT_EMBEDDED_VERSION).tar.xz
MOONLIGHT_EMBEDDED_SITE = https://github.com/irtimmer/moonlight-embedded/releases/download/v$(MOONLIGHT_EMBEDDED_VERSION)
MOONLIGHT_EMBEDDED_DEPENDENCIES = opus expat libevdev avahi alsa-lib udev libcurl libcec ffmpeg sdl2 libenet

MOONLIGHT_EMBEDDED_CONF_OPTS = "-DCMAKE_INSTALL_SYSCONFDIR=/etc"

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	MOONLIGHT_EMBEDDED_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_LIBAMCODEC),y)
	MOONLIGHT_EMBEDDED_DEPENDENCIES += libamcodec
endif

$(eval $(cmake-package))
