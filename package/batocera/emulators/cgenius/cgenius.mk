################################################################################
#
# Commander Genius
#
################################################################################

CGENIUS_VERSION = a4d906de6b6b9a517f5a22d33d85467e3bfb8b9e
CGENIUS_SITE = https://github.com/gerstrong/Commander-Genius
CGENIUS_SITE_METHOD = git

CGENIUS_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf boost

# No OpenGL ES support
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
CGENIUS_CONF_OPTS += -DUSE_OPENGL=ON
else
CGENIUS_CONF_OPTS += -DUSE_OPENGL=OFF
endif

$(eval $(cmake-package))
