################################################################################
#
# PPSSPP
#
################################################################################
# Version.: Commits on Dec 5, 2017
PPSSPP15_VERSION = v1.5.4
PPSSPP15_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP15_SITE_METHOD=git
PPSSPP15_GIT_SUBMODULES=YES
PPSSPP15_DEPENDENCIES = sdl2 zlib libzip zip ffmpeg

# x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	PPSSPP15_CONF_OPTS += -DX86=ON
endif

# x86_64
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	PPSSPP15_CONF_OPTS += -DX86_64=ON
endif

# odroid c2 / S905 and variants
ifeq ($(BR2_aarch64),y)
	# -DUSE_SYSTEM_FFMPEG=1 is unstable, but at least, games without videos work
	PPSSPP15_CONF_OPTS += -DUSE_FFMPEG=ON -DUSE_SYSTEM_FFMPEG=ON
else
	PPSSPP15_CONF_OPTS += -DUSE_FFMPEG=ON
endif

# odroid xu4 legacy
ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK),y)
	PPSSPP15_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON
	# odroid xu4
	ifeq ($(BR2_PACKAGE_SDL2_KMSDRM),y)
	PPSSPP15_CONF_OPTS += -DUSING_EGL=OFF
	endif
endif

# rpi1 / rpi2 /rp3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP15_DEPENDENCIES += rpi-userland
	PPSSPP15_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DRASPBIAN=ON
endif

ifeq ($(BR2_aarch64)$(BR2_ARM_CPU_HAS_NEON),y)
	PPSSPP15_CONF_OPTS += -DARM_NEON=ON
endif

# odroid xu4 / rpi3
ifeq ($(BR2_arm),y)
	PPSSPP15_CONF_OPTS += -DARMV7=ON
endif

# s912 (libhybris)
ifeq ($(BR2_PACKAGE_LIBHYBRIS),y)
	PPSSPP15_CONF_OPTS += -DUSING_FBDEV=ON -DUSING_GLES2=ON -DUSING_EGL=ON
endif

define PPSSPP15_UPDATE_INCLUDES
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
	sed -i 's/unknown/$(PPSSPP15_VERSION)/g' $(@D)/git-version.cmake
endef

PPSSPP15_PRE_CONFIGURE_HOOKS += PPSSPP15_UPDATE_INCLUDES

define PPSSPP15_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	cp -R $(@D)/assets $(TARGET_DIR)/usr/bin
endef

$(eval $(cmake-package))