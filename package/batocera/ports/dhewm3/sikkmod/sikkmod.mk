################################################################################
#
# sikkmod
#
################################################################################
# Version: Commits on Jun 8, 2026
SIKKMOD_VERSION = 8dd804c33eed764ef96887dd7f1f42f64eebd7f8
SIKKMOD_SITE = $(call github,dhewm,dhewm3-sdk,$(SIKKMOD_VERSION))
SIKKMOD_LICENSE = GPLv3
SIKKMOD_LICENSE_FILES = COPYING.txt

SIKKMOD_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define SIKKMOD_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/sikkmod*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
