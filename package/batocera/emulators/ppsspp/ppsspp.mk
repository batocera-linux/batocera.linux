################################################################################
#
# PPSSPP
#
################################################################################
# Version.: Commits on Mar 14, 2019
PPSSPP_VERSION = v1.8.0
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_LICENSE = GPLv2
PPSSPP_DEPENDENCIES = sdl2 libzip ffmpeg

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
	# -DUSE_SYSTEM_FFMPEG=1 is unstable, but at least, games without videos work
	PPSSPP_CONF_OPTS += -DUSE_FFMPEG=ON -DARM_NEON=ON
else
	PPSSPP_CONF_OPTS += -DUSE_FFMPEG=ON
endif

# odroid xu4 / odroid xu4 legacy / odroid n2
ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK)$(BR2_PACKAGE_MALI_HKG52FBDEV)$(BR2_PACKAGE_MALI_BIFROST),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=OFF -DUSING_X11_VULKAN=OFF
endif

# rpi1 / rpi2 /rp3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP_DEPENDENCIES += rpi-userland
	PPSSPP_CONF_OPTS += -DRASPBIAN=ON -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=ON -DUSING_X11_VULKAN=OFF
endif

# odroid xu4 / rpi3 / rockpro64
ifeq ($(BR2_arm),y)
	PPSSPP_CONF_OPTS += -DARMV7=ON 
endif

# s912 (libhybris)
ifeq ($(BR2_PACKAGE_LIBHYBRIS),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=OFF -DUSING_X11_VULKAN=OFF
endif

# rockpro64
ifeq ($(BR2_PACKAGE_MALI_RK450)$(BR2_PACKAGE_MALI_T760),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=OFF -DUSING_X11_VULKAN=OFF -DUSE_WAYLAND_WSI=OFF
endif

define PPSSPP_UPDATE_INCLUDES
	sed -i 's/unknown/$(PPSSPP_VERSION)/g' $(@D)/git-version.cmake
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_UPDATE_INCLUDES

define PPSSPP_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	cp -R $(@D)/assets $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/lib
	cp -R $(@D)/lib/*.so $(TARGET_DIR)/lib
endef

$(eval $(cmake-package))
