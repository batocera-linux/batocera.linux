################################################################################
#
# perfected
#
################################################################################
# Version: Commits on Jun 8, 2026
PERFECTED_VERSION = 0976ee154cf62d9fb01a5b8456020acf32ff92ac
PERFECTED_SITE = $(call github,dhewm,dhewm3-sdk,$(PERFECTED_VERSION))
PERFECTED_LICENSE = GPLv3
PERFECTED_LICENSE_FILES = COPYING.txt

PERFECTED_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define PERFECTED_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/perfected*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
