################################################################################
#
# cemu
#
################################################################################

CEMU_MAJOR = 2
CEMU_MINOR = 1
CEMU_PATCH = 
ifneq ($(CEMU_PATCH),)
CEMU_VERSION = v$(CEMU_MAJOR).$(CEMU_MINOR)-$(CEMU_PATCH)
else
CEMU_VERSION = v$(CEMU_MAJOR).$(CEMU_MINOR)
endif
CEMU_SITE = https://github.com/cemu-project/Cemu
CEMU_LICENSE = GPLv2
CEMU_SITE_METHOD=git
CEMU_GIT_SUBMODULES=YES
CEMU_DEPENDENCIES = sdl2 host-libcurl host-pugixml pugixml rapidjson boost libpng \
                    libzip host-glslang glslang zlib zstd wxwidgets fmt glm \
					host-nasm host-zstd host-libusb

CEMU_SUPPORTS_IN_SOURCE_BUILD = NO

CEMU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CEMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CEMU_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
CEMU_CONF_OPTS += -DENABLE_VCPKG=OFF
CEMU_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include/glslang"
CEMU_CONF_OPTS += -DENABLE_FERAL_GAMEMODE=OFF
CEMU_CONF_OPTS += -DEMULATOR_VERSION_MAJOR=$(CEMU_MAJOR)
CEMU_CONF_OPTS += -DEMULATOR_VERSION_MINOR=$(CEMU_MINOR)
ifneq ($(CEMU_PATCH),)
CEMU_CONF_OPTS += -DEMULATOR_VERSION_PATCH=$(CEMU_PATCH)
endif

ifeq ($(BR2_PACKAGE_HIDAPI),y)
    CEMU_CONF_OPTS += -DENABLE_HIDAPI=ON
    CEMU_DEPENDENCIES += hidapi
else
    CEMU_CONF_OPTS += -DENABLE_HIDAPI=OFF
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    CEMU_CONF_OPTS += -DENABLE_WAYLAND=ON
    CEMU_DEPENDENCIES += wayland wayland-protocols
else
    CEMU_CONF_OPTS += -DENABLE_WAYLAND=OFF
endif

define CEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/cemu/
	mv -f $(@D)/bin/Cemu_release $(@D)/bin/cemu
	cp -pr $(@D)/bin/{cemu,gameProfiles,resources} $(TARGET_DIR)/usr/bin/cemu/
	$(INSTALL) -m 0755 -D \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/get-audio-device \
	    $(TARGET_DIR)/usr/bin/cemu/
	# keys.txt
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu
	touch $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu/keys.txt
	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/wiiu.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
