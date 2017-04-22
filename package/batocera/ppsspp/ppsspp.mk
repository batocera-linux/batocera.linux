################################################################################
#
# PPSSPP
#
################################################################################
PPSSPP_VERSION = 3eaa81570443506a1e8dd26217c7700854628a77
#PPSSPP_SITE = $(call github,hrydgard,ppsspp,$(PPSSPP_VERSION))
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_DEPENDENCIES = sdl2 zlib libzip zip ffmpeg

# required at least on x86
ifeq ($(BR2_PACKAGE_LIBGLU),y)
PPSSPP_DEPENDENCIES += libglu
endif

define PPSSPP_CONFIGURE_PI
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_CONFIGURE_PI

define PPSSPP_INSTALL_TO_TARGET
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	cp -R $(@D)/assets $(TARGET_DIR)/usr/bin
endef

PPSSPP_INSTALL_TARGET_CMDS = $(PPSSPP_INSTALL_TO_TARGET)

ifeq ($(BR2_aarch64),y)
# -DUSE_SYSTEM_FFMPEG=1 is unstable, but at least, games without videos work
PPSSPP_CONF_OPTS += -DUSE_FFMPEG=1 -DUSE_SYSTEM_FFMPEG=1
else
PPSSPP_CONF_OPTS += -DUSE_FFMPEG=1
endif

ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK),y)
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=1
	PPSSPP_CONF_OPTS += -DUSING_GLES2=1
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP_DEPENDENCIES += rpi-userland
	PPSSPP_CONF_OPTS += -DUSING_FBDEV=1
	PPSSPP_CONF_OPTS += -DUSING_GLES2=1
endif

ifeq ($(BR2_aarch64)$(BR2_ARM_CPU_HAS_NEON),y)
	PPSSPP_CONF_OPTS += -DARM_NEON=1
endif

# odroid xu4 / rpi3
ifeq ($(BR2_arm),y)
	PPSSPP_CONF_OPTS += -DARMV7=1
endif

$(eval $(cmake-package))
