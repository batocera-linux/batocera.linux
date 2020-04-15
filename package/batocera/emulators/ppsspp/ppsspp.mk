################################################################################
#
# PPSSPP
#
################################################################################
# Version.: Commits on Apr 9, 2020 ( v1.9.4 )
PPSSPP_VERSION = 7d3552ae34591eb0768e84c0148f566307abea1e
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_LICENSE = GPLv2
PPSSPP_DEPENDENCIES = sdl2 libzip ffmpeg

PPSSPP_CONF_OPTS = -DUSE_FFMPEG=ON -DCMAKE_BUILD_TYPE=Release -DUSE_DISCORD=OFF

# x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	PPSSPP_CONF_OPTS += -DX86=ON
endif

# x86_64
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	PPSSPP_CONF_OPTS += -DX86_64=ON
endif

# odroid c2 / S905 and variants
ifeq ($(BR2_aarch64),y)
	PPSSPP_CONF_OPTS += -DARM_NEON=ON -DUSING_X11_VULKAN=OFF 
endif

# odroid / rpi / rockpro64
ifeq ($(BR2_arm),y)
	PPSSPP_CONF_OPTS += -DARMV7=ON -DUSING_X11_VULKAN=OFF 
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=OFF -DUSE_WAYLAND_WSI=OFF
endif

# rpi1 / rpi2 /rp3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP_DEPENDENCIES += rpi-userland
	PPSSPP_CONF_OPTS += -DRASPBIAN=ON -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=ON
endif

# s912 (libhybris)
ifeq ($(BR2_PACKAGE_LIBHYBRIS),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=OFF
endif

define PPSSPP_UPDATE_INCLUDES
	sed -i 's/unknown/$(PPSSPP_VERSION)/g' $(@D)/git-version.cmake
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_UPDATE_INCLUDES

define PPSSPP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/ppsspp
	cp -R $(@D)/assets $(TARGET_DIR)/usr/share/ppsspp/PPSSPP
	mkdir -p $(TARGET_DIR)/lib
	cp -R $(@D)/lib/*.so $(TARGET_DIR)/lib
endef

$(eval $(cmake-package))
