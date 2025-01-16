################################################################################
#
# fitz
#
################################################################################
# Version: Commits on Apr 19, 2024
FITZ_VERSION = 41cfd224f9c3d4ba9b3882aae8c349efa4ae7148
FITZ_SITE = $(call github,dhewm,dhewm3-sdk,$(FITZ_VERSION))
FITZ_LICENSE = GPLv3
FITZ_LICENSE_FILES = COPYING.txt

FITZ_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define FITZ_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/fitz*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
