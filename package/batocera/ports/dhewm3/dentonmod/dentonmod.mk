################################################################################
#
# dentonmod
#
################################################################################
# Version: Commits on Jun 8, 2026
DENTONMOD_VERSION = 9342a53e63e2b281735241f4bff67bcd7612a7b5
DENTONMOD_SITE = $(call github,dhewm,dhewm3-sdk,$(DENTONMOD_VERSION))
DENTONMOD_LICENSE = GPLv3
DENTONMOD_LICENSE_FILES = COPYING.txt

DENTONMOD_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

DENTONMOD_CONF_OPTS = -DBASE_NAME=dentonmod

define DENTONMOD_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/dentonmod*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
