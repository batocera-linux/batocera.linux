################################################################################
#
# realgibs
#
################################################################################
# Version: Commits on Jun 8, 2026
REALGIBS_VERSION = 83e0a5b96cba2fa36a22b8930245e482d4c36902
REALGIBS_SITE = $(call github,dhewm,dhewm3-sdk,$(REALGIBS_VERSION))
REALGIBS_LICENSE = GPLv3
REALGIBS_LICENSE_FILES = COPYING.txt

REALGIBS_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define REALGIBS_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/realgibs*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
