################################################################################
#
# libretro-vircon32
#
################################################################################
# Version: 1.3 Commits on Aug 29, 2024
LIBRETRO_VIRCON32_VERSION = v1.3
LIBRETRO_VIRCON32_SITE = https://github.com/vircon32/vircon32-libretro
LIBRETRO_VIRCON32_SITE_METHOD = git
LIBRETRO_VIRCON32_GIT_SUBMODULES = YES
LIBRETRO_VIRCON32_LICENSE = 3-Clause BSD

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    LIBRETRO_VIRCON32_DEPENDENCIES += libgl
    LIBRETRO_VIRCON32_CONF_OPTS += -DENABLE_OPENGL=1
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    LIBRETRO_VIRCON32_DEPENDENCIES += libgles
    LIBRETRO_VIRCON32_CONF_OPTS += -DENABLE_OPENGLES3=1
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    LIBRETRO_VIRCON32_DEPENDENCIES += libgles
    LIBRETRO_VIRCON32_CONF_OPTS += -DENABLE_OPENGLES2=1
endif


define LIBRETRO_VIRCON32_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vircon32_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vircon32_libretro.so
endef

$(eval $(cmake-package))
