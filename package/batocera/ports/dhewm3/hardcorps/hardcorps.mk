################################################################################
#
# hardcorps
#
################################################################################
# Version: Commits on Apr 19, 2024
HARDCORPS_VERSION = d8d797c2481169743a8907c67f161b059f072a26
HARDCORPS_SITE = $(call github,dhewm,dhewm3-sdk,$(HARDCORPS_VERSION))
HARDCORPS_LICENSE = GPLv3
HARDCORPS_LICENSE_FILES = COPYING.txt

HARDCORPS_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define HARDCORPS_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/hardcorps*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
