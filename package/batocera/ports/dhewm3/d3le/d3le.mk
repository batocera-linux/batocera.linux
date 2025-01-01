################################################################################
#
# d3le
#
################################################################################
# Version: Commits on Apr 19, 2024
D3LE_VERSION = 0e6e3519b21eae4690810180210cc90b0174dc3d
D3LE_SITE = $(call github,dhewm,dhewm3-sdk,$(D3LE_VERSION))
D3LE_LICENSE = GPLv3
D3LE_LICENSE_FILES = COPYING.txt

D3LE_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

D3LE_CONF_OPTS = -DBASE=OFF -DD3XP_NAME=d3le -DD3XP=ON

define D3LE_INSTALL_TARGET_CMDS 
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/d3le.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
