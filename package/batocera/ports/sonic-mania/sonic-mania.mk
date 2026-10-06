################################################################################
#
# sonic-mania
#
################################################################################

SONIC_MANIA_VERSION = v1.1.1
SONIC_MANIA_SITE = https://github.com/RSDKModding/Sonic-Mania-Decompilation
SONIC_MANIA_SITE_METHOD = git
SONIC_MANIA_GIT_SUBMODULES = YES
SONIC_MANIA_LICENSE = Proprietary
SONIC_MANIA_LICENSE_FILE = LICENSE.md
SONIC_MANIA_EMULATOR_INFO = sonic-mania.emulator.yml

SONIC_MANIA_DEPENDENCIES += libglu libglew libglfw libogg libtheora portaudio sdl2

SONIC_MANIA_SUPPORTS_IN_SOURCE_BUILD = NO

SONIC_MANIA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONIC_MANIA_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SONIC_MANIA_CONF_OPTS += -DGAME_STATIC=ON
SONIC_MANIA_CONF_OPTS += -DUSE_SDL_AUDIO=ON
SONIC_MANIA_CONF_OPTS += -DRETRO_OUTPUT_NAME=sonic-mania

define SONIC_MANIA_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/dependencies/RSDKv5/sonic-mania \
	    $(TARGET_DIR)/usr/bin/sonic-mania
	# OpenGL shaders aren't in Data.rsdk, so ship them as a mod like upstream does
	mkdir -p $(TARGET_DIR)/usr/share/sonic-mania/mods/GLShaders/Data/Shaders/OGL
	$(INSTALL) -m 0644 $(@D)/dependencies/RSDKv5/RSDKv5/Shaders/OGL/* \
	    $(TARGET_DIR)/usr/share/sonic-mania/mods/GLShaders/Data/Shaders/OGL/
	printf "Name=GLShaders\nDescription=OGLShaders\nAuthor=Ducky\nVersion=1.0.0\nTargetVersion=-1\n" \
	    > $(TARGET_DIR)/usr/share/sonic-mania/mods/GLShaders/mod.ini
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
