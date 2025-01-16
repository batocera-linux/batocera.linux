################################################################################
#
# desolated
#
################################################################################
# Version: Commits on Oct 21, 2024
DESOLATED_VERSION = ee6addacfe721e587c3b2c9a2594953cd9c774bc
DESOLATED_SITE = $(call github,dhewm,dhewm3-sdk,$(DESOLATED_VERSION))
DESOLATED_LICENSE = GPLv3
DESOLATED_LICENSE_FILES = COPYING.txt

DESOLATED_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define DESOLATED_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/desolated*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
