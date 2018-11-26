################################################################################
#
# PPSSPP
#
################################################################################
# Version.: Commits on Nov 23, 2018
PPSSPP_VERSION = v1.7.4
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_DEPENDENCIES = sdl2 zlib libzip zip ffmpeg

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
	PPSSPP_CONF_OPTS += -DUSE_FFMPEG=ON -DUSE_SYSTEM_FFMPEG=ON -DARM_NEON=ON
else
	PPSSPP_CONF_OPTS += -DUSE_FFMPEG=ON
endif

# odroid xu4
ifeq ($(BR2_PACKAGE_SDL2_KMSDRM),y)
	PPSSPP_CONF_OPTS += -DUSING_EGL=OFF -DUSING_X11_VULKAN=OFF
endif

# odroid xu4 legacy
ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=ON -DUSING_X11_VULKAN=OFF
endif

# rpi1 / rpi2 /rp3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP_DEPENDENCIES += rpi-userland
	PPSSPP_CONF_OPTS += -DRASPBIAN=ON -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=ON -DUSING_X11_VULKAN=OFF
endif

# odroid xu4 / rpi3
ifeq ($(BR2_arm),y)
	PPSSPP_CONF_OPTS += -DARMV7=ON
endif

# s912 (libhybris)
ifeq ($(BR2_PACKAGE_LIBHYBRIS),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=OFF -DUSING_X11_VULKAN=OFF
endif

define PPSSPP_UPDATE_INCLUDES
	sed -i 's/unknown/$(PPSSPP_VERSION)/g' $(@D)/git-version.cmake
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_UPDATE_INCLUDES

define PPSSPP_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	cp -R $(@D)/assets $(TARGET_DIR)/usr/bin
	cp -R $(@D)/lib/*.so $(TARGET_DIR)/lib
endef

$(eval $(cmake-package))
