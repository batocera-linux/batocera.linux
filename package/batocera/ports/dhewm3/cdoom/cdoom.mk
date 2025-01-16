################################################################################
#
# cdoom
#
################################################################################
# Version: Commits on Apr 19, 2024
CDOOM_VERSION = c6d2afac06b3b0b16e2efc7e23e27c60822eefa9
CDOOM_SITE = $(call github,dhewm,dhewm3-sdk,$(CDOOM_VERSION))
CDOOM_LICENSE = GPLv3
CDOOM_LICENSE_FILES = COPYING.txt

CDOOM_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define CDOOM_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/cdoom*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
