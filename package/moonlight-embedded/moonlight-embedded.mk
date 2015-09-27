################################################################################
#
# moonlight-embedded
#
################################################################################

MOONLIGHT_EMBEDDED_VERSION = 2.1.1
MOONLIGHT_EMBEDDED_SOURCE = moonlight-embedded-$(MOONLIGHT_EMBEDDED_VERSION).tar.xz
MOONLIGHT_EMBEDDED_SITE = https://github.com/irtimmer/moonlight-embedded/releases/download/v$(MOONLIGHT_EMBEDDED_VERSION)
MOONLIGHT_EMBEDDED_DEPENDENCIES = opus expat libevdev avahi alsa-lib udev libcurl libcec ffmpeg sdl2

define MOONLIGHT_EMBEDDED_EXTRACT_CMDS
	$(TAR) -xf $(DL_DIR)/$(MOONLIGHT_EMBEDDED_SOURCE) -C $(BUILD_DIR)
endef

MOONLIGHT_EMBEDDED_CONF_OPTS = "-DCMAKE_INSTALL_SYSCONFDIR=/etc"

$(eval $(cmake-package))
