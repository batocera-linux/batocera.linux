#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
################################################################################
#
# lindbergh-loader
#
################################################################################

LINDBERGH_LOADER_VERSION = v2.1.4
LINDBERGH_LOADER_SITE = $(call github,lindbergh-loader,lindbergh-loader,$(LINDBERGH_LOADER_VERSION))
LINDBERGH_LOADER_LICENSE = ShareAlike 4.0 International
LINDBERGH_LOADER_LICENSE_FILES = LICENSE.md
LINDBERGH_LOADER_EMULATOR_INFO = lindbergh-loader.emulator.yml

ifeq ($(BR2_x86_64),y)
LINDBERGH_LOADER_DEPENDENCIES = wine-x86 dmidecode ossp
endif

ifeq ($(BR2_i386),y)
LINDBERGH_LOADER_DEPENDENCIES += alsa-lib alsa-plugins alsa-utils faudio libfreeglut
LINDBERGH_LOADER_DEPENDENCIES += pcsc-lite libbsd libglew sdl3 sdl3_image sdl3_ttf
LINDBERGH_LOADER_DEPENDENCIES += ncurses openal pipewire udev xlib_libX11 xlib_libXext   
LINDBERGH_LOADER_DEPENDENCIES += xlib_libXi xlib_libXmu xlib_libXScrnSaver

LINDBERGH_LOADER_CFLAGS += -g -fPIC -m32 -pthread -Wall -Werror -Wno-misleading-indentation
LINDBERGH_LOADER_CFLAGS += -Wno-unused-but-set-variable -Wno-unused-variable
LINDBERGH_LOADER_CFLAGS += -Wno-unused-function -D_GNU_SOURCE -Wno-char-subscripts
LINDBERGH_LOADER_CFLAGS += -I$(STAGING_DIR)/usr/include

LINDBERGH_LOADER_LDFLAGS += -m32 -Wl,-z,defs -rdynamic -static-libgcc -lc -ldl -lGL -lglut -lX11
LINDBERGH_LOADER_LDFLAGS += -lXcursor -lSDL3 -lSDL3_image -lSDL3_ttf -ludev -lm -lpthread
LINDBERGH_LOADER_LDFLAGS += -shared -nostdlib -lasound -lxdiff -lFAudio -L./src/libxdiff
LINDBERGH_LOADER_LDFLAGS += -L$(STAGING_DIR)/usr/lib

define LINDBERGH_LOADER_BUILD_CMDS
    $(MAKE) \
		CC="$(TARGET_CC)" \
		CFLAGS_FOR_BUILD="-I$(STAGING_DIR)/usr/include" \
		CFLAGS="$(LINDBERGH_LOADER_CFLAGS)" \
		CXX="$(TARGET_CXX)" \
		CPPFLAGS="-I$(STAGING_DIR)/usr/include" \
		LDFLAGS="$(LINDBERGH_LOADER_LDFLAGS)" \
		AR="$(TARGET_AR)" \
		-C $(@D) all
endef

define LINDBERGH_LOADER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/lindbergh
	mkdir -p $(TARGET_DIR)/usr/bin/lindbergh/extralibs
	cp -fv $(@D)/build/* $(TARGET_DIR)/usr/bin/lindbergh/
	cp -fv $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lindbergh-loader/*.ini \
	    $(TARGET_DIR)/usr/bin/lindbergh/
	cp -fv $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lindbergh-loader/lib*.so* \
	    $(TARGET_DIR)/usr/bin/lindbergh/extralibs
endef
endif

$(eval $(generic-package))
$(eval $(emulator-info-package))
