################################################################################
#
# eoc
#
################################################################################
# Version: Commits on Jun 7, 2026
EOC_VERSION = d97448a28c6234e060dd75a158b4357fa5801b8a
EOC_SITE = $(call github,dhewm,dhewm3-sdk,$(EOC_VERSION))
EOC_LICENSE = GPLv3
EOC_LICENSE_FILES = COPYING.txt

EOC_DEPENDENCIES = dhewm3 host-libjpeg libcurl libogg libvorbis openal sdl2 zlib

define EOC_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib/dhewm3
	cp $(@D)/eoc*.so $(TARGET_DIR)/usr/lib/dhewm3/
endef

$(eval $(cmake-package))
