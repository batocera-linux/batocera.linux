################################################################################
#
# DOLPHIN_EMU
#
################################################################################

DOLPHIN_EMU_VERSION = 5.0
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_DEPENDENCIES = xserver_xorg-server libevdev ffmpeg zlib libpng lzo libusb libcurl sfml

# bluez is disable otherwise a compilation error appears
DOLPHIN_EMU_CONF_OPTS = -DDISABLE_WX=1 -DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/include

$(eval $(cmake-package))
