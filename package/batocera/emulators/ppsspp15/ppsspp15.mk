################################################################################
#
# PPSSPP15 - Package created for RPI3 due to the low performance of version 1.6.3
#
################################################################################
# Version.: committed on Dec 20, 2017 (v1.5.4)
PPSSPP15_VERSION = c27d64f273c231241e84498eb9392fbc05635780
PPSSPP15_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP15_SITE_METHOD=git
PPSSPP15_GIT_SUBMODULES=YES
PPSSPP15_DEPENDENCIES = sdl2 zlib libzip zip ffmpeg

# rpi3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP15_DEPENDENCIES += rpi-userland
	PPSSPP15_CONF_OPTS += -DRASPBIAN=ON -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSE_FFMPEG=ON -DARMV7=ON
endif

define PPSSPP15_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	cp -R $(@D)/assets $(TARGET_DIR)/usr/bin
endef

$(eval $(cmake-package))
