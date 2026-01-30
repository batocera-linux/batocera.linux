################################################################################
#
# cemu-android
#
################################################################################

CEMU_ANDROID_MAJOR = 0
CEMU_ANDROID_MINOR = 03
CEMU_ANDROID_PATCH = 
ifneq ($(CEMU_ANDROID_PATCH),)
CEMU_ANDROID_VERSION = $(CEMU_ANDROID_MAJOR).$(CEMU_ANDROID_MINOR)-$(CEMU_ANDROID_PATCH)
else
CEMU_ANDROID_VERSION = $(CEMU_ANDROID_MAJOR).$(CEMU_ANDROID_MINOR)
endif
CEMU_ANDROID_SITE = https://github.com/SSimco/Cemu
CEMU_ANDROID_LICENSE = GPLv2
CEMU_ANDROID_SITE_METHOD = git
CEMU_ANDROID_GIT_SUBMODULES = YES

CEMU_ANDROID_DEPENDENCIES = bluez5_utils boost fmt glslang glm host-doxygen host-nasm \
                    libcurl libgtk3 libopenssl libpng libusb libzip libzlib \
                    pulseaudio pugixml rapidjson sdl2 speexdsp wxwidgets zstd \
                    host-clang host-ninja host-lld

CEMU_ANDROID_SUPPORTS_IN_SOURCE_BUILD = NO

CEMU_ANDROID_CMAKE_BACKEND = ninja

CEMU_ANDROID_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CEMU_ANDROID_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CEMU_ANDROID_CONF_OPTS += -DLINUX=ON -DCMAKE_SYSTEM_NAME=Linux
CEMU_ANDROID_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
CEMU_ANDROID_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
CEMU_ANDROID_CONF_OPTS += -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON
CEMU_ANDROID_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=lld -no-pie -lm -lstdc++"
CEMU_ANDROID_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
CEMU_ANDROID_CONF_OPTS += -DENABLE_VCPKG=OFF
CEMU_ANDROID_CONF_OPTS += -DENABLE_FERAL_GAMEMODE=OFF
CEMU_ANDROID_CONF_OPTS += -DENABLE_WXWIDGETS=ON
CEMU_ANDROID_CONF_OPTS += -DENABLE_BLUEZ=ON
CEMU_ANDROID_CONF_OPTS += -DALLOW_PORTABLE=OFF
CEMU_ANDROID_CONF_OPTS += -DEMULATOR_VERSION_MAJOR=$(CEMU_ANDROID_MAJOR)
CEMU_ANDROID_CONF_OPTS += -DEMULATOR_VERSION_MINOR=$(CEMU_ANDROID_MINOR)
ifneq ($(CEMU_ANDROID_PATCH),)
CEMU_ANDROID_CONF_OPTS += -DEMULATOR_VERSION_PATCH=$(CEMU_ANDROID_PATCH)
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
    CEMU_ANDROID_DEPENDENCIES += xlib_libX11 xlib_libXext
endif

ifeq ($(BR2_PACKAGE_LIBGLVND),y)
    CEMU_ANDROID_DEPENDENCIES += libglvnd
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    CEMU_ANDROID_DEPENDENCIES += libgl
    CEMU_ANDROID_CONF_OPTS += -DENABLE_OPENGL=ON
else
    CEMU_ANDROID_CONF_OPTS += -DENABLE_OPENGL=OFF
endif

ifeq ($(BR2_PACKAGE_HIDAPI),y)
    CEMU_ANDROID_CONF_OPTS += -DENABLE_HIDAPI=ON
    CEMU_ANDROID_DEPENDENCIES += hidapi
else
    CEMU_ANDROID_CONF_OPTS += -DENABLE_HIDAPI=OFF
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    CEMU_ANDROID_CONF_OPTS += -DENABLE_WAYLAND=ON
    CEMU_ANDROID_DEPENDENCIES += wayland wayland-protocols
else
    CEMU_ANDROID_CONF_OPTS += -DENABLE_WAYLAND=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    CEMU_ANDROID_CONF_OPTS += -DENABLE_VULKAN=ON
    CEMU_ANDROID_DEPENDENCIES += vulkan-headers vulkan-loader
else
    CEMU_ANDROID_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

define CEMU_ANDROID_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/cemu/
	mv -f $(@D)/bin/Cemu_release $(@D)/bin/cemu
	cp -pr $(@D)/bin/{cemu,gameProfiles,resources} $(TARGET_DIR)/usr/bin/cemu/
	$(INSTALL) -m 0755 -D \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/get-audio-device \
	    $(TARGET_DIR)/usr/bin/cemu/
	# create dir for keys.txt
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/cemu
endef

$(eval $(cmake-package))
