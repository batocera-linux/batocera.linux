################################################################################
#
# rivensin
#
################################################################################
# Version: Commits on Jun 8, 2026
RIVENSIN_VERSION = a4dfc7ca5f338df50eac83806e123f88121d58a5
RIVENSIN_SITE = $(call github,dhewm,dhewm3-sdk,$(RIVENSIN_VERSION))
RIVENSIN_LICENSE = GPLv3
RIVENSIN_LICENSE_FILES = COPYING.txt

RIVENSIN_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define RIVENSIN_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/rivensin*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
