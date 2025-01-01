################################################################################
#
# dhewm3
#
################################################################################
# Version: Commits on Dec 4, 2024
DHEWM3_VERSION = ce4e6f076f3ebbfd4c71021773c90c13ecdc79df
DHEWM3_SITE = $(call github,dhewm,dhewm3,$(DHEWM3_VERSION))
DHEWM3_LICENSE = GPLv3
DHEWM3_LICENSE_FILES = COPYING.txt
DHEWM3_SUBDIR = neo

DHEWM3_DEPENDENCIES = host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

define DHEWM3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/dhewm3/doom3.dhewm3.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

DHEWM3_POST_INSTALL_TARGET_HOOKS = DHEWM3_EVMAPY

$(eval $(cmake-package))
