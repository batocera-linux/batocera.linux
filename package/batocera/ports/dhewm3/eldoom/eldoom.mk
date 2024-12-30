################################################################################
#
# eldoom
#
################################################################################
# Version: Commits on Oct 22, 2024
ELDOOM_VERSION = 50dc874961cf14d3c7ca2182d655ba46ecc7f5a1
ELDOOM_SITE = $(call github,dhewm,dhewm3-sdk,$(ELDOOM_VERSION))
ELDOOM_LICENSE = GPLv3
ELDOOM_LICENSE_FILES = COPYING.txt

ELDOOM_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define ELDOOM_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/eldoom*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
