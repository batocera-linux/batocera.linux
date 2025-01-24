################################################################################
#
# lindbergh-loader
#
################################################################################
# Version: Commits on Jan 12, 2025
LINDBERGH_LOADER_VERSION = 59212c742e4b5c958977dd37c1f7a16e9a1227c7
LINDBERGH_LOADER_SITE = $(call github,dmanlfc,lindbergh-loader,$(LINDBERGH_LOADER_VERSION))
LINDBERGH_LOADER_LICENSE = ShareAlike 4.0 International
LINDBERGH_LOADER_LICENSE_FILES = LICENSE.md

ifeq ($(BR2_x86_64),y)
LINDBERGH_LOADER_DEPENDENCIES = wine-x86
endif

ifeq ($(BR2_i386),y)
LINDBERGH_LOADER_DEPENDENCIES += alsa-lib alsa-plugins alsa-utils faudio libfreeglut pcsc-lite
LINDBERGH_LOADER_DEPENDENCIES += libglew sdl2 ncurses openal pipewire xlib_libX11 libbsd
LINDBERGH_LOADER_DEPENDENCIES += xlib_libXext xlib_libXi xlib_libXmu xlib_libXScrnSaver  

# match the makefile cflags
LINDBERGH_LOADER_CFLAGS = -g -fPIC -m32 -Wall -Werror -Wno-unused-but-set-variable
LINDBERGH_LOADER_CFLAGS += -Wno-unused-variable -Wno-unused-function -D_GNU_SOURCE
LINDBERGH_LOADER_CFLAGS += -Wno-char-subscripts -Wno-misleading-indentation
LINDBERGH_LOADER_CFLAGS += -I$(STAGING_DIR)/usr/include
# match the makefile ldflags
LINDBERGH_LOADER_LDFLAGS += -L$(STAGING_DIR)/usr/lib
LINDBERGH_LOADER_LDFLAGS += -Wl,-z,defs -rdynamic -static-libgcc -lc -ldl -lGL
LINDBERGH_LOADER_LDFLAGS += -lglut -lX11 -lSDL2 -lFAudio -lm -lpthread -shared
LINDBERGH_LOADER_LDFLAGS += -nostdlib -lasound -L./src/libxdiff -lxdiff

define LINDBERGH_LOADER_BUILD_CMDS
    $(MAKE) \
	CC="$(HOSTCC) -m32 -pthread" \
	CFLAGS_FOR_BUILD="-I$(STAGING_DIR)/usr/include" \
	CFLAGS="$(LINDBERGH_LOADER_CFLAGS)" \
	CPPFLAGS="-I$(STAGING_DIR)/usr/include" \
	LD="$(TARGET_CC) -m32" \
	LDFLAGS="$(LINDBERGH_LOADER_LDFLAGS)" \
	-C $(@D) all
endef

define LINDBERGH_LOADER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/lindbergh
	mkdir -p $(TARGET_DIR)/usr/bin/lindbergh/extralibs
	cp -fv $(@D)/build/* $(TARGET_DIR)/usr/bin/lindbergh/
	cp -fv $(@D)/docs/lindbergh.conf $(TARGET_DIR)/usr/bin/lindbergh/
	cp -fv $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lindbergh-loader/lib*.so* \
	    $(TARGET_DIR)/usr/bin/lindbergh/extralibs
endef
endif

define LINDBERGH_LOADER_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lindbergh-loader/lindbergh.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

ifeq ($(BR2_x86_64),y)
LINDBERGH_LOADER_POST_INSTALL_TARGET_HOOKS = LINDBERGH_LOADER_EVMAPY
endif

$(eval $(generic-package))
