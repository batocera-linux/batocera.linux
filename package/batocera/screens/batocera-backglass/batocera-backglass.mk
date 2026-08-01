################################################################################
#
# batocera-backglass
#
################################################################################

BATOCERA_BACKGLASS_VERSION = 1.0
BATOCERA_BACKGLASS_LICENSE = GPL
BATOCERA_BACKGLASS_SOURCE =

BATOCERA_BACKGLASS_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf libcurl openssl

BACKGLASS_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/batocera-backglass

define BATOCERA_BACKGLASS_BUILD_CMDS
	$(TARGET_CXX) $(TARGET_CXXFLAGS) $(TARGET_LDFLAGS) \
		-o $(@D)/batocera-backglass-window \
		$(BACKGLASS_PATH)/batocera-backglass-window.cpp \
		-lSDL2 -lSDL2_image -lSDL2_ttf -lcurl -lcrypto -lpthread
endef

define BATOCERA_BACKGLASS_INSTALL_TARGET_CMDS
	# Install main bash controls script
	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 $(BACKGLASS_PATH)/batocera-backglass.sh \
		$(TARGET_DIR)/usr/bin/batocera-backglass
	
	# Install the compiled native backglass execution window binary
	install -m 0755 $(@D)/batocera-backglass-window \
		$(TARGET_DIR)/usr/bin/batocera-backglass-window

	# Install hook wrappers
	mkdir -p $(TARGET_DIR)/usr/share/batocera-backglass/scripts
	$(INSTALL) -m 0755 -D $(BACKGLASS_PATH)/scripts/*.sh \
		$(TARGET_DIR)/usr/share/batocera-backglass/scripts/
endef

$(eval $(generic-package))
