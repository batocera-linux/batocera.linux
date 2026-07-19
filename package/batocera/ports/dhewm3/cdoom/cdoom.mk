################################################################################
#
# cdoom
#
################################################################################
# Version: Commits on Jun 8, 2026
CDOOM_VERSION = 60f24e4fe4bf758fe92010654f633572fcbcec9d
CDOOM_SITE = $(call github,dhewm,dhewm3-sdk,$(CDOOM_VERSION))
CDOOM_LICENSE = GPLv3
CDOOM_LICENSE_FILES = COPYING.txt

CDOOM_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define CDOOM_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/cdoom*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
