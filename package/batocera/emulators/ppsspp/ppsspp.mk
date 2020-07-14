################################################################################
#
# PPSSPP
#
################################################################################
# Version.: Commits on Jul 12, 2020
PPSSPP_VERSION = v1.10.3
PPSSPP_SITE = https://github.com/hrydgard/ppsspp.git
PPSSPP_SITE_METHOD=git
PPSSPP_GIT_SUBMODULES=YES
PPSSPP_LICENSE = GPLv2
PPSSPP_DEPENDENCIES = sdl2 libzip ffmpeg

PPSSPP_CONF_OPTS = -DUSE_FFMPEG=ON -DUSING_FBDEV=ON -DUSE_WAYLAND_WSI=OFF \
		   -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Linux -DUSE_DISCORD=OFF \
		   -DUSING_X11_VULKAN=OFF -DARM_NO_VULKAN=ON

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
	PPSSPP_CONF_OPTS += -DARM64=ON
	PPSSPP_CONF_OPTS += -DUSING_GLES2=ON -DUSING_EGL=ON
endif

# odroid / rpi / rockpro64
ifeq ($(BR2_arm),y)
	PPSSPP_CONF_OPTS += -DARMV7=ON -DARM=ON
	PPSSPP_CONF_OPTS += -DUSING_GLES2=ON
endif

# rockchip
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKCHIP_ANY),y)
	PPSSPP_CONF_OPTS += \
		-DANDROID=OFF -DWIN32=OFF -DAPPLE=OFF \
		-DUSE_SYSTEM_FFMPEG=ON -DCMAKE_CROSSCOMPILING=ON \
		-DVULKAN=OFF -DUSING_EGL=OFF \
		-DUSING_QT_UI=OFF -DUNITTEST=OFF -DSIMULATOR=OFF -DHEADLESS=OFF

	# In order to support the custom resolution patch, permissive compile is needed
	PPSSPP_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(COMPILER_COMMONS_CXXFLAGS_EXE) -fpermissive"
else
	ifeq ($(BR2_arm),y)
		PPSSPP_CONF_OPTS += -DUSING_EGL=ON
	endif
endif

# rpi1 / rpi2 /rp3
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PPSSPP_DEPENDENCIES += rpi-userland
	PPSSPP_CONF_OPTS += -DPPSSPP_PLATFORM_RPI=1
endif

# s912 (libhybris)
ifeq ($(BR2_PACKAGE_LIBHYBRIS),y)
	PPSSPP_CONF_OPTS += -DUSING_GLES2=ON -DUSING_EGL=OFF
endif

define PPSSPP_UPDATE_INCLUDES
	sed -i 's/unknown/$(PPSSPP_VERSION)/g' $(@D)/git-version.cmake
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
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
