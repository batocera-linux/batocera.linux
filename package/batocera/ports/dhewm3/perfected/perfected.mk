################################################################################
#
# perfected
#
################################################################################
# Version: Commits on Jul 29, 2024
PERFECTED_VERSION = 20a7240238f9dcd4864e841343550b18605ac34a
PERFECTED_SITE = $(call github,dhewm,dhewm3-sdk,$(PERFECTED_VERSION))
PERFECTED_LICENSE = GPLv3
PERFECTED_LICENSE_FILES = COPYING.txt

PERFECTED_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define PERFECTED_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/perfected*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
