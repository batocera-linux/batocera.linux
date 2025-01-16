################################################################################
#
# sikkmod
#
################################################################################
# Version: Commits on Jul 29, 2024
SIKKMOD_VERSION = 03aae2f5b74a18ed5fdbfe9c345a4d50203c7518
SIKKMOD_SITE = $(call github,dhewm,dhewm3-sdk,$(SIKKMOD_VERSION))
SIKKMOD_LICENSE = GPLv3
SIKKMOD_LICENSE_FILES = COPYING.txt

SIKKMOD_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define SIKKMOD_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/sikkmod*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
