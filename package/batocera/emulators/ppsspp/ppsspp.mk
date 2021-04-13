################################################################################
#
# PPSSPP
#
################################################################################
# Version: March 2, 2021
PPSSPP_VERSION = v1.11.3
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_LICENSE = GPLv2
PPSSPP_DEPENDENCIES = sdl2 libzip ffmpeg

PPSSPP_CONF_OPTS = \
	-DUSE_FFMPEG=ON -DUSE_SYSTEM_FFMPEG=ON -DUSING_FBDEV=ON -DUSE_WAYLAND_WSI=OFF \
	-DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Linux -DUSE_DISCORD=OFF \
	-DBUILD_SHARED_LIBS=OFF -DANDROID=OFF -DWIN32=OFF -DAPPLE=OFF \
	-DUNITTEST=OFF -DSIMULATOR=OFF

PPSSPP_TARGET_CFLAGS = $(TARGET_CFLAGS)

ifeq ($(BR2_PACKAGE_QT5),y)
PPSSPP_CONF_OPTS += -DUSING_QT_UI=ON
PPSSPP_TARGET_BINARY = PPSSPPQt
else
PPSSPP_CONF_OPTS += -DUSING_QT_UI=OFF
PPSSPP_TARGET_BINARY = PPSSPPSDL
endif

# make sure to select glvnd and depends on glew / glu because of X11 desktop GL
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
	PPSSPP_CONF_OPTS += -DOpenGL_GL_PREFERENCE=GLVND
	PPSSPP_DEPENDENCIES += libglew libglu
endif

# enable vulkan if we are building with it
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
	PPSSPP_CONF_OPTS += -DVULKAN=ON
else
	PPSSPP_CONF_OPTS += -DVULKAN=OFF
endif

# enable x11/vulkan interface only if xorg
ifeq ($(BR2_PACKAGE_XORG7),y)
	PPSSPP_CONF_OPTS += -DUSING_X11_VULKAN=ON
else
	PPSSPP_CONF_OPTS += -DUSING_X11_VULKAN=OFF
	PPSSPP_TARGET_CFLAGS += -DEGL_NO_X11=1 -DMESA_EGL_NO_X11_HEADERS=1
endif

# x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	PPSSPP_CONF_OPTS += -DX86=ON
endif

# x86_64
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	PPSSPP_CONF_OPTS += -DX86_64=ON
endif

# rpi4 / odroidgoa
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4)$(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	PPSSPP_CONF_OPTS += -DARM_NO_VULKAN=OFF
else
	PPSSPP_CONF_OPTS += -DARM_NO_VULKAN=ON
endif

# odroid c2 / S905 and variants
ifeq ($(BR2_aarch64),y)
PPSSPP_CONF_OPTS += \
	-DARM64=ON \
	-DUSING_GLES2=ON \
	-DUSING_EGL=ON
endif

# odroid / rpi / rockpro64
ifeq ($(BR2_arm),y)
PPSSPP_CONF_OPTS += \
	-DARMV7=ON \
	-DARM=ON \
	-DUSING_GLES2=ON
endif

# rockchip
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKCHIP_ANY),y)
ifeq ($(BR2_arm),y)
PPSSPP_CONF_OPTS += -DUSING_EGL=OFF
endif

# In order to support the custom resolution patch, permissive compile is needed
PPSSPP_TARGET_CFLAGS += -fpermissive
else
ifeq ($(BR2_arm),y)
PPSSPP_CONF_OPTS += -DUSING_EGL=ON
endif
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
PPSSPP_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

# rpi1 / rpi2 /rp3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP_DEPENDENCIES += rpi-userland
	PPSSPP_CONF_OPTS += -DPPSSPP_PLATFORM_RPI=1
endif

PPSSPP_CONF_OPTS += -DCMAKE_C_FLAGS="$(PPSSPP_TARGET_CFLAGS)" -DCMAKE_CXX_FLAGS="$(PPSSPP_TARGET_CFLAGS)"

define PPSSPP_UPDATE_INCLUDES
	sed -i 's/unknown/$(PPSSPP_VERSION)/g' $(@D)/git-version.cmake
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_UPDATE_INCLUDES

define PPSSPP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(@D)/$(PPSSPP_TARGET_BINARY) $(TARGET_DIR)/usr/bin/PPSSPP
	mkdir -p $(TARGET_DIR)/usr/share/ppsspp
	cp -R $(@D)/assets $(TARGET_DIR)/usr/share/ppsspp/PPSSPP
endef

$(eval $(cmake-package))
