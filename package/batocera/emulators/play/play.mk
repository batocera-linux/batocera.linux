################################################################################
#
# PLAY
#
################################################################################

PLAY_VERSION = 0.51
PLAY_SITE = https://github.com/jpd002/Play-.git
PLAY_LICENSE = BSD
PLAY_DEPENDENCIES = qt5base qt5x11extras xserver_xorg-server libglew vulkan-headers vulkan-loader

PLAY_SITE_METHOD = git
PLAY_GIT_SUBMODULES = YES

PLAY_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PLAY_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
PLAY_CONF_OPTS += -DBUILD_TESTS=OFF
PLAY_CONF_OPTS += -DENABLE_AMAZON_S3=ON
# Force to use GLES on ARM
#PLAY_CONF_OPTS += -DUSE_GLEW=OFF
#PLAY_CONF_OPTS += -DUSE_GLES=ON

define PLAY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/Source/ui_qt/Play \
		$(TARGET_DIR)/usr/bin/play-emu
	$(INSTALL) -D $(@D)/Source/ui_qt/Source/CodeGen/libCodeGen.so \
		$(TARGET_DIR)/usr/lib/libCodeGen.so
	$(INSTALL) -D $(@D)/Source/ui_qt/Source/Framework/libFramework.so \
		$(TARGET_DIR)/usr/lib/libFramework.so
	$(INSTALL) -D $(@D)/Source/ui_qt/gs/GSH_OpenGL/FrameworkOpenGl/libFramework_OpenGl.so \
		$(TARGET_DIR)/usr/lib/libFramework_OpenGl.so
	$(INSTALL) -D $(@D)/Source/ui_qt/gs/GSH_Vulkan/FrameworkVulkan/libFramework_Vulkan.so \
		$(TARGET_DIR)/usr/lib/libFramework_Vulkan.so
	$(INSTALL) -D $(@D)/Source/ui_qt/gs/GSH_Vulkan/Nuanceur/libNuanceur.so \
		$(TARGET_DIR)/usr/lib/libNuanceur.so
	$(INSTALL) -D $(@D)/Source/ui_qt/SH_OpenAL/FrameworkOpenAl/libFramework_OpenAl.so \
		$(TARGET_DIR)/usr/lib/libFramework_OpenAl.so
	$(INSTALL) -D $(@D)/Source/ui_qt/Source/FrameworkAmazon/libFramework_Amazon.so \
		$(TARGET_DIR)/usr/lib/libFramework_Amazon.so
	$(INSTALL) -D $(@D)/Source/ui_qt/Source/FrameworkAmazon/FrameworkHttp/libFramework_Http.so \
		$(TARGET_DIR)/usr/lib/libFramework_Http.so

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/play/ps2.play.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
