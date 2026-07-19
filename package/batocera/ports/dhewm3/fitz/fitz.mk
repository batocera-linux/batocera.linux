################################################################################
#
# fitz
#
################################################################################
# Version: Commits on Jun 8, 2026
FITZ_VERSION = 81ca7a947a3a4996094be25a3be2f3a25a62c34b
FITZ_SITE = $(call github,dhewm,dhewm3-sdk,$(FITZ_VERSION))
FITZ_LICENSE = GPLv3
FITZ_LICENSE_FILES = COPYING.txt

FITZ_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define FITZ_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/fitz*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
