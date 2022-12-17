################################################################################
#
# ppsspp
#
################################################################################

PPSSPP_VERSION = v1.14
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_LICENSE = GPLv2
PPSSPP_DEPENDENCIES = sdl2 libzip

PPSSPP_CONF_OPTS = \
	-DUSE_FFMPEG=ON -DUSE_SYSTEM_FFMPEG=OFF -DUSING_FBDEV=ON -DUSE_WAYLAND_WSI=OFF \
	-DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Linux -DUSE_DISCORD=OFF \
	-DBUILD_SHARED_LIBS=OFF -DANDROID=OFF -DWIN32=OFF -DAPPLE=OFF \
	-DUNITTEST=OFF -DSIMULATOR=OFF -DUSING_QT_UI=OFF -DHEADLESS=ON -DMOBILE_DEVICE=OFF

PPSSPP_TARGET_CFLAGS = $(TARGET_CFLAGS)
PPSSPP_TARGET_BINARY = PPSSPPSDL

# make sure to select glvnd and depends on glew / glu because of X11 desktop GL
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
    PPSSPP_CONF_OPTS += -DOpenGL_GL_PREFERENCE=GLVND
    PPSSPP_DEPENDENCIES += libglew libglu
endif

# enable vulkan if we are building with it
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    PPSSPP_CONF_OPTS += -DVULKAN=ON -DUSE_VULKAN_DISPLAY_KHR=ON
else
    PPSSPP_CONF_OPTS += -DVULKAN=OFF
endif
# enable x11/vulkan interface only if xorg
ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    PPSSPP_CONF_OPTS += -DUSING_X11_VULKAN=ON
else
    PPSSPP_CONF_OPTS += -DUSING_X11_VULKAN=OFF
    PPSSPP_TARGET_CFLAGS += -DEGL_NO_X11=1 -DMESA_EGL_NO_X11_HEADERS=1
endif

# arm
ifeq ($(BR2_arm),y)
    PPSSPP_CONF_OPTS += -DARM=ON
    PPSSPP_CONF_OPTS += -DARMV7=ON
    PPSSPP_CONF_OPTS += -DUSING_GLES2=ON
    PPSSPP_CONF_OPTS += -DUSING_EGL=OFF
endif

ifeq ($(BR2_aarch64),y)
    PPSSPP_CONF_OPTS += -DARM=ON
    PPSSPP_CONF_OPTS += -DARM64=ON
    PPSSPP_CONF_OPTS += -DUSING_GLES2=ON
    PPSSPP_CONF_OPTS += -DUSING_EGL=OFF
endif

# x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
    PPSSPP_CONF_OPTS += -DX86=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    PPSSPP_CONF_OPTS += -DX86_64=ON
endif

# rpi4 and panfrost vulkan support
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_PANFROST_MESA3D),y)
    PPSSPP_CONF_OPTS += -DARM_NO_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
    PPSSPP_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

PPSSPP_CONF_OPTS += -DCMAKE_C_FLAGS="$(PPSSPP_TARGET_CFLAGS)" -DCMAKE_CXX_FLAGS="$(PPSSPP_TARGET_CFLAGS)"

define PPSSPP_UPDATE_INCLUDES
	sed -i 's/unknown/"$(shell echo $(PPSSPP_VERSION) | cut -c 1-7)"/g' $(@D)/git-version.cmake
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_UPDATE_INCLUDES

define PPSSPP_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    $(INSTALL) -D -m 0755 $(@D)/$(PPSSPP_TARGET_BINARY) $(TARGET_DIR)/usr/bin/PPSSPP
    mkdir -p $(TARGET_DIR)/usr/share/ppsspp
    cp -R $(@D)/assets $(TARGET_DIR)/usr/share/ppsspp/PPSSPP
    # Fix PSP font for languages like Japanese
    # (font from https://github.com/minoryorg/Noto-Sans-CJK-JP/blob/master/fonts/)
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ppsspp/NotoSansCJKjp-DemiLight.ttf $(TARGET_DIR)/usr/share/ppsspp/PPSSPP/Roboto-Condensed.ttf
endef

$(eval $(cmake-package))
