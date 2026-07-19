################################################################################
#
# desolated
#
################################################################################
# Version: Commits on Jun 8, 2026
DESOLATED_VERSION = e5501815ca7181b52432c4620dcd48ed2fa62402
DESOLATED_SITE = $(call github,dhewm,dhewm3-sdk,$(DESOLATED_VERSION))
DESOLATED_LICENSE = GPLv3
DESOLATED_LICENSE_FILES = COPYING.txt

DESOLATED_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define DESOLATED_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/desolated*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
