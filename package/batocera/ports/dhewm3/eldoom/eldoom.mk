################################################################################
#
# eldoom
#
################################################################################
# Version: Commits on Jun 8, 2026
ELDOOM_VERSION = e6461952e6d2dc882ad06d365ec78c7c0eebcce4
ELDOOM_SITE = $(call github,dhewm,dhewm3-sdk,$(ELDOOM_VERSION))
ELDOOM_LICENSE = GPLv3
ELDOOM_LICENSE_FILES = COPYING.txt

ELDOOM_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define ELDOOM_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/eldoom*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
