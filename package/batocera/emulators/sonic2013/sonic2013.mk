
SONIC2013_VERSION = '759d8459638a4fa97fb7c8729029369b90dcbe87'
SONIC2013_SITE = $(call github,Rubberduckycooly,Sonic-1-2-2013-Decompilation,$(SONIC2013_VERSION))
SONIC2013_DEPENDENCIES = sdl2 libogg libvorbis
SONIC2013_LICENSE = Custom

define SONIC2013_BUILD_CMDS
	rm -rf $(@D)/tmp
	rm -rf $(@D)/dependencies/all/asio/
	git clone https://github.com/chriskohlhoff/asio.git $(@D)/tmp
	mv $(@D)/tmp/* $(@D)/dependencies/all/
	rm -rf $(@D)/tmp
	rm -rf $(@D)/dependencies/all/tinyxml2
	git clone https://github.com/leethomason/tinyxml2.git $(@D)/dependencies/all/tinyxml2
	rm -rf $(@D)/dependencies/all/stb-image
	git clone https://github.com/nothings/stb.git $(@D)/dependencies/all/stb-image
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile VERBOSE=1
endef

define SONIC2013_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/RSDKv4 $(TARGET_DIR)/usr/bin/sonic2013
endef

define SONIC2013_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy $(TARGET_DIR)/usr/share/sonic2013
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/sonic2013/sonicretro.sonic2013.keys $(TARGET_DIR)/usr/share/evmapy
endef

SONIC2013_POST_INSTALL_TARGET_HOOKS += SONIC2013_POST_PROCESS

$(eval $(generic-package))