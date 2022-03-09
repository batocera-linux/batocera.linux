################################################################################
#
# libretro-flycast
#
################################################################################
# Version: Commits on Feb 28, 2022
LIBRETRO_FLYCAST_VERSION = 830ffd0559eafc2954ffc957e7e7323a9421ca55
LIBRETRO_FLYCAST_SITE = https://github.com/flyinghead/flycast.git
LIBRETRO_FLYCAST_SITE_METHOD=git
LIBRETRO_FLYCAST_GIT_SUBMODULES=YES
LIBRETRO_FLYCAST_LICENSE = GPLv2
LIBRETRO_FLYCAST_DEPENDENCIES = retroarch

LIBRETRO_FLYCAST_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_FLYCAST_CONF_OPTS = -DUSE_OPENMP=ON -DLIBRETRO=ON \
    -DUSE_OPENGL=ON -DBUILD_SHARED_LIBS=OFF -DBUILD_EXTERNAL=OFF

# determine the best GLES version to use - prefer GLES3
ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    LIBRETRO_FLYCAST_CONF_OPTS += -DUSE_GLES=ON -DUSE_GLES2=OFF
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    LIBRETRO_FLYCAST_CONF_OPTS += -DUSE_GLES2=ON -DUSE_GLES=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    LIBRETRO_FLYCAST_CONF_OPTS += -DUSE_VULKAN=ON
else
    LIBRETRO_FLYCAST_CONF_OPTS += -DUSE_VULKAN=OFF
endif

# RPI: use the legacy Broadcom GLES libraries
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    LIBRETRO_FLYCAST_CONF_OPTS += -DUSE_VIDEOCORE
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
    LIBRETRO_FLYCAST_CONF_OPTS += -DUSE_MALI=ON
endif

define LIBRETRO_FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/flycast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/flycast_libretro.so
endef

$(eval $(cmake-package))
