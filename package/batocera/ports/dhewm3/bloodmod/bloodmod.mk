################################################################################
#
# bloodmod
#
################################################################################
# Version: Commits on Sep 27, 2024
BLOODMOD_VERSION = f35e2718939b68c75f2f3a07749554129e049c30
BLOODMOD_SITE = $(call github,dhewm,dhewm3-sdk,$(BLOODMOD_VERSION))
BLOODMOD_LICENSE = GPLv3
BLOODMOD_LICENSE_FILES = COPYING.txt

BLOODMOD_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define BLOODMOD_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/bloodmod.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
