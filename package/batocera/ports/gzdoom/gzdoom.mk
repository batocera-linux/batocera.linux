################################################################################
#
# GZDOOM
#
################################################################################

GZDOOM_VERSION = g4.7.1
GZDOOM_SITE = https://github.com/coelckers/gzdoom.git
GZDOOM_SITE_METHOD=git
GZDOOM_GIT_SUBMODULES=YES
GZDOOM_LICENSE = GPL v3
GZDOOM_DEPENDENCIES = sdl2 zmusic

GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DDYN_GTK=OFF -DDYN_OPENAL=OFF

GZDOOM_CONF_ENV += ZMUSIC_LIBRARIES="/x86_64/target/usr/lib/" ZMUSIC_INCLUDE_DIR="/x86_64/target/usr/lib/cmake/ZMusic/"

#GZDOOM_CONF_ENV += LDFLAGS="-lpthread -lvorbisfile -lopusfile -lFLAC -lmodplug -lfluidsynth"

define GZDOOM_INSTALL_TARGET_CMDS
		mkdir -p $(TARGET_DIR)/usr/bin
		mkdir -p $(TARGET_DIR)/usr/lib/gzdoom
		mkdir -p $(TARGET_DIR)/usr/share/gzdoom
	$(INSTALL) -D -m 0755 $(@D)/gzdoom $(TARGET_DIR)/usr/bin/gzdoom
	cp -a $(@D)/gzdoom.pk3 $(TARGET_DIR)/usr/lib/gzdoom/
	cp -a $(@D)/game_support.pk3 $(TARGET_DIR)/usr/lib/gzdoom/
	cp -a $(@D)/brightmaps.pk3 $(TARGET_DIR)/usr/share/gzdoom/
	cp -a $(@D)/game_widescreen_gfx.pk3 $(TARGET_DIR)/usr/share/gzdoom/
	cp -a $(@D)/lights.pk3 $(TARGET_DIR)/usr/share/gzdoom/
	cp -pr $(@D)/fm_banks $(TARGET_DIR)/usr/share/gzdoom/
	cp -pr $(@D)/soundfonts $(TARGET_DIR)/usr/share/gzdoom/

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/gzdoom/gzdoom.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
