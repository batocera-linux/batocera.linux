################################################################################
#
# grimm
#
################################################################################
# Version: Commits on Nov 13, 2024
GRIMM_VERSION = 009b958e4adaadc081b4953fe2ac4d8eb1db6917
GRIMM_SITE = $(call github,dhewm,dhewm3-sdk,$(GRIMM_VERSION))
GRIMM_LICENSE = GPLv3
GRIMM_LICENSE_FILES = COPYING.txt

GRIMM_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define GRIMM_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/grimm*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
