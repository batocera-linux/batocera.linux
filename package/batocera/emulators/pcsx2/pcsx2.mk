################################################################################
#
# pcsx2
#
################################################################################
#Version: Commits on Nov 5, 2022
PCSX2_VERSION = v1.7.3527
PCSX2_SITE = https://github.com/pcsx2/pcsx2.git
PCSX2_SITE_METHOD = git
PCSX2_GIT_SUBMODULES = YES
PCSX2_SUPPORTS_IN_SOURCE_BUILD = NO
PCSX2_LICENSE = GPLv3
PCSX2_LICENSE_FILE = COPYING.GPLv3
PCSX2_DEPENDENCIES = xserver_xorg-server alsa-lib freetype zlib libpng wxwidgets
PCSX2_DEPENDENCIES += libaio portaudio libsoundtouch sdl2 libpcap yaml-cpp libgtk3
PCSX2_DEPENDENCIES += libsamplerate fmt

PCSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PCSX2_CONF_OPTS += -DXDG_STD=TRUE
PCSX2_CONF_OPTS += -DSDL2_API=TRUE
PCSX2_CONF_OPTS += -DDISABLE_PCSX2_WRAPPER=1
PCSX2_CONF_OPTS += -DPACKAGE_MODE=FALSE
PCSX2_CONF_OPTS += -DwxWidgets_CONFIG_EXECUTABLE="$(STAGING_DIR)/usr/bin/wx-config"
PCSX2_CONF_OPTS += -DPCSX2_TARGET_ARCHITECTURES=x86_64
PCSX2_CONF_OPTS += -DENABLE_TESTS=OFF
PCSX2_CONF_OPTS += -DEXTRA_PLUGINS=TRUE
PCSX2_CONF_OPTS += -DQT_BUILD=FALSE
PCSX2_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
# auto will use system libraries & fallback to 3rd party
PCSX2_CONF_OPTS += -DUSE_SYSTEM_LIBS=AUTO
PCSX2_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON
PCSX2_CONF_OPTS += -DUSE_VTUNE=OFF
PCSX2_CONF_OPTS += -DUSE_VULKAN=ON
PCSX2_CONF_OPTS += -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=TRUE

define PCSX2_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/buildroot-build/pcsx2/pcsx2 $(TARGET_DIR)/usr/pcsx2/bin/pcsx2
	cp -pr  $(@D)/bin/resources $(TARGET_DIR)/usr/pcsx2/bin/
	mkdir -p $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/common/libcommon.so $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/glad/libglad.so $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/imgui/libimgui.so $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/rapidyaml/rapidyaml/libryml.so.0.4.1 $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/glslang/libglslang.so $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/zstd/libpcsx2-zstd.so $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/jpgd/libjpgd.so $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/cubeb/libcubeb.so.0 $(TARGET_DIR)/usr/pcsx2/lib
	cp -p $(@D)/buildroot-build/3rdparty/cpuinfo/libcpuinfo.so $(TARGET_DIR)/usr/pcsx2/lib
endef

define PCSX2_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/pcsx2/ps2.pcsx2.keys $(TARGET_DIR)/usr/share/evmapy
endef

PCSX2_POST_INSTALL_TARGET_HOOKS += PCSX2_EVMAPY

$(eval $(cmake-package))
