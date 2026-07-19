################################################################################
#
# hardcorps
#
################################################################################
# Version: Commits on Jun 8, 2026
HARDCORPS_VERSION = b767e8cf42428e9aa32817cc4456f5bfe8ed8262
HARDCORPS_SITE = $(call github,dhewm,dhewm3-sdk,$(HARDCORPS_VERSION))
HARDCORPS_LICENSE = GPLv3
HARDCORPS_LICENSE_FILES = COPYING.txt

HARDCORPS_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define HARDCORPS_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/hardcorps*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
