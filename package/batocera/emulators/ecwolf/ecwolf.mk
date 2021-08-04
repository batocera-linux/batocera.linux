################################################################################
#
# ECWOLF
#
################################################################################
# Version.: Commits on Feb 16, 2021
ECWOLF_VERSION = 3ce6e4d064b54eec72386fe949ec7be20746c16c
ECWOLF_SITE = https://bitbucket.org/ecwolf/ecwolf.git
ECWOLF_SITE_METHOD=git
ECWOLF_GIT_SUBMODULES=YES
ECWOLF_LICENSE = Non-commercial
ECWOLF_DEPENDENCIES = sdl2

ECWOLF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DGPL=ON

ECWOLF_CONF_ENV += LDFLAGS="-lpthread -lvorbisfile -lopusfile -lFLAC -lmodplug -lfluidsynth"

define ECWOLF_INSTALL_TARGET_CMDS
		mkdir -p $(TARGET_DIR)/usr/bin
		mkdir -p $(TARGET_DIR)/usr/share/ecwolf
	$(INSTALL) -D -m 0755 $(@D)/ecwolf $(TARGET_DIR)/usr/share/ecwolf/ecwolf
	cp -a $(@D)/ecwolf.pk3 $(TARGET_DIR)/usr/share/ecwolf/
	ln -sf /usr/share/ecwolf/ecwolf $(TARGET_DIR)/usr/bin/ecwolf

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ecwolf/ecwolf.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
