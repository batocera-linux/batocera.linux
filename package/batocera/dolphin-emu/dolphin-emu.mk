################################################################################
#
# DOLPHIN_EMU
#
################################################################################

# 5.0 + pad name bug fixed
DOLPHIN_EMU_VERSION = 63d5e573371611118ce199a423121eac5218ba0c
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_DEPENDENCIES = xserver_xorg-server libevdev ffmpeg zlib libpng lzo libusb libcurl sfml bluez5_utils wxwidgets hidapi

# bluez is disable otherwise a compilation error appears
DOLPHIN_EMU_CONF_OPTS = -DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/include -DENABLE_QT2=False

$(eval $(cmake-package))
