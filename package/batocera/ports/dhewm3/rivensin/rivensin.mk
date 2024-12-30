################################################################################
#
# rivensin
#
################################################################################
# Version: Commits on Apr 19, 2024
RIVENSIN_VERSION = 4416ef0f7ebb4f9dd0e68442404621204ab5fdde
RIVENSIN_SITE = $(call github,dhewm,dhewm3-sdk,$(RIVENSIN_VERSION))
RIVENSIN_LICENSE = GPLv3
RIVENSIN_LICENSE_FILES = COPYING.txt

RIVENSIN_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define RIVENSIN_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/rivensin*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
