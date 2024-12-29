################################################################################
#
# realgibs
#
################################################################################
# Version: Commits on Sep 27, 2024
REALGIBS_VERSION = 85d79f0565420a4e22598feecc84d3786a5a510d
REALGIBS_SITE = $(call github,dhewm,dhewm3-sdk,$(REALGIBS_VERSION))
REALGIBS_LICENSE = GPLv3
REALGIBS_LICENSE_FILES = COPYING.txt

REALGIBS_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define REALGIBS_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/realgibs*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
