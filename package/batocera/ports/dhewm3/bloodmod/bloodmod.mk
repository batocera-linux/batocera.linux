################################################################################
#
# bloodmod
#
################################################################################
# Version: Commits on Jun 8, 2026
BLOODMOD_VERSION = 67bc24c623232efd947f9005026f7ac6dabc62d9
BLOODMOD_SITE = $(call github,dhewm,dhewm3-sdk,$(BLOODMOD_VERSION))
BLOODMOD_LICENSE = GPLv3
BLOODMOD_LICENSE_FILES = COPYING.txt

BLOODMOD_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define BLOODMOD_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/bloodmod.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
