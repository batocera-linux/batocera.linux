################################################################################
#
# grimm
#
################################################################################
# Version: Commits on Jun 8, 2026
GRIMM_VERSION = 34cb764c9e618c3073ed645ac71666559334bb17
GRIMM_SITE = $(call github,dhewm,dhewm3-sdk,$(GRIMM_VERSION))
GRIMM_LICENSE = GPLv3
GRIMM_LICENSE_FILES = COPYING.txt

GRIMM_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define GRIMM_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/grimm*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
