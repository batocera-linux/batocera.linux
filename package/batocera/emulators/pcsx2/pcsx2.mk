################################################################################
#
# PCSX2
#
################################################################################

PCSX2_VERSION = c783b6d7b56916f62de53e50828355b214159a08
PCSX2_SITE = $(call github,pcsx2,pcsx2,$(PCSX2_VERSION))
PCSX2_DEPENDENCIES = xserver_xorg-server alsa-lib freetype zlib libpng wxwidgets libaio portaudio libsoundtouch sdl2

PCSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PCSX2_CONF_OPTS += -DXDG_STD=TRUE
PCSX2_CONF_OPTS += -DDISABLE_PCSX2_WRAPPER=1
PCSX2_CONF_OPTS += -DwxWidgets_CONFIG_EXECUTABLE="$(STAGING_DIR)/usr/bin/wx-config"

#define PCSX2_REMOVE_DOUBLEPATH_INSTALL
#	echo mv $(TARGET_DIR)/$()
#	exit 1
#endef

#PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_REMOVE_DOUBLEPATH_INSTALL

$(eval $(cmake-package))
