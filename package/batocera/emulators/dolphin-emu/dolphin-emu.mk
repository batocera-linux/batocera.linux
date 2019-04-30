################################################################################
#
# DOLPHIN_EMU
#
################################################################################
# Version.: Commits on May 23, 2018
DOLPHIN_EMU_VERSION = a60bba37cd208cf365a6c6cf4f0f17c6fea8e169
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_LICENSE = GPLv2+
DOLPHIN_EMU_DEPENDENCIES = xserver_xorg-server libevdev ffmpeg zlib libpng lzo libusb libcurl sfml bluez5_utils wxwidgets hidapi

# bluez is disable otherwise a compilation error appears
DOLPHIN_EMU_CONF_OPTS = -DBUILD_SHARED_LIBS=OFF -DOPENGL_INCLUDE_DIR=$(STAGING_DIR)/usr/include -DENABLE_QT2=False

$(eval $(cmake-package))
