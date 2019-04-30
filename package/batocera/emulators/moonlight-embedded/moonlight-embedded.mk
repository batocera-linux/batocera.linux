################################################################################
#
# moonlight-embedded
#
################################################################################
# Version.: Commits on Apr 18, 2019 (v2.4.7)
MOONLIGHT_EMBEDDED_VERSION = 7b46b4b2ea4e51bc758a02d18cf80313ba442161
MOONLIGHT_EMBEDDED_SITE = git://github.com/irtimmer/moonlight-embedded.git
MOONLIGHT_EMBEDDED_GIT_SUBMODULES=y
MOONLIGHT_EMBEDDED_LICENSE = GPLv3
MOONLIGHT_EMBEDDED_DEPENDENCIES = opus expat libevdev avahi alsa-lib udev libcurl libcec ffmpeg sdl2 libenet

MOONLIGHT_EMBEDDED_CONF_OPTS = "-DCMAKE_INSTALL_SYSCONFDIR=/etc"

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	MOONLIGHT_EMBEDDED_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_LIBAMCODEC),y)
	MOONLIGHT_EMBEDDED_DEPENDENCIES += libamcodec
endif

$(eval $(cmake-package))
