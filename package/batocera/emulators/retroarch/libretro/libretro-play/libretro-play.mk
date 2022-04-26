################################################################################
#
# libretro-play
#
################################################################################

LIBRETRO_PLAY_VERSION = 0.51
LIBRETRO_PLAY_SITE = https://github.com/jpd002/Play-.git
LIBRETRO_PLAY_LICENSE = BSD
LIBRETRO_PLAY_DEPENDENCIES = qt5base qt5x11extras xserver_xorg-server libglew

LIBRETRO_PLAY_SITE_METHOD = git
LIBRETRO_PLAY_GIT_SUBMODULES = YES

LIBRETRO_PLAY_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_TESTS=OFF
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_LIBRETRO_CORE=ON
LIBRETRO_PLAY_CONF_OPTS += -DBUILD_PLAY=OFF
LIBRETRO_PLAY_CONF_OPTS += -DENABLE_AMAZON_S3=ON
# Force to use GLES on ARM
#LIBRETRO_PLAY_CONF_OPTS += -DUSE_GLEW=OFF
#LIBRETRO_PLAY_CONF_OPTS += -DUSE_GLES=ON

define LIBRETRO_PLAY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Source/ui_libretro/play_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/play_libretro.so
	$(INSTALL) -D $(@D)/Source/ui_libretro/Source/CodeGen/libCodeGen.so \
		$(TARGET_DIR)/usr/lib/libCodeGen.so
	$(INSTALL) -D $(@D)/Source/ui_libretro/Source/Framework/libFramework.so \
		$(TARGET_DIR)/usr/lib/libFramework.so
	$(INSTALL) -D $(@D)/Source/ui_libretro/gs/GSH_OpenGL/FrameworkOpenGl/libFramework_OpenGl.so \
		$(TARGET_DIR)/usr/lib/libFramework_OpenGl.so
	$(INSTALL) -D $(@D)/Source/ui_libretro/Source/FrameworkAmazon/libFramework_Amazon.so \
		$(TARGET_DIR)/usr/lib/libFramework_Amazon.so
	$(INSTALL) -D $(@D)/Source/ui_libretro/Source/FrameworkAmazon/FrameworkHttp/libFramework_Http.so \
		$(TARGET_DIR)/usr/lib/libFramework_Http.so
endef

$(eval $(cmake-package))
