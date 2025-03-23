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
# Version: Commits on Mar 14, 2025
LINDBERGH_LOADER_VERSION = a96b1fcf30b1110981468aee7bab9eec174a3153
LINDBERGH_LOADER_SITE = $(call github,lindbergh-loader,lindbergh-loader,$(LINDBERGH_LOADER_VERSION))
LINDBERGH_LOADER_LICENSE = ShareAlike 4.0 International
LINDBERGH_LOADER_LICENSE_FILES = LICENSE.md

ifeq ($(BR2_x86_64),y)
LINDBERGH_LOADER_DEPENDENCIES = wine-x86 dmidecode
endif

ifeq ($(BR2_i386),y)
LINDBERGH_LOADER_DEPENDENCIES += alsa-lib alsa-plugins alsa-utils faudio libfreeglut pcsc-lite
LINDBERGH_LOADER_DEPENDENCIES += libglew sdl2 ncurses openal pipewire xlib_libX11 libbsd
LINDBERGH_LOADER_DEPENDENCIES += xlib_libXext xlib_libXi xlib_libXmu xlib_libXScrnSaver  

# match the makefile cflags
LINDBERGH_LOADER_CFLAGS += -g -fPIC -m32 -pthread -Wall -Werror -Wno-misleading-indentation
LINDBERGH_LOADER_CFLAGS += -Wno-unused-but-set-variable -Wno-unused-variable
LINDBERGH_LOADER_CFLAGS += -Wno-unused-function -D_GNU_SOURCE -Wno-char-subscripts
LINDBERGH_LOADER_CFLAGS += -I$(STAGING_DIR)/usr/include
# match the makefile ldflags
LINDBERGH_LOADER_LDFLAGS += -m32 -Wl,-z,defs -rdynamic -static-libgcc -lc -ldl -lGL
LINDBERGH_LOADER_LDFLAGS += -lglut -lX11 -lXcursor -lSDL2 -lm -lpthread -shared
LINDBERGH_LOADER_LDFLAGS += -nostdlib -lasound -L./src/libxdiff -lxdiff -lFAudio
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
	cp -fv $(@D)/docs/lindbergh.conf $(TARGET_DIR)/usr/bin/lindbergh/
	cp -fv $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/lindbergh-loader/lib*.so* \
	    $(TARGET_DIR)/usr/bin/lindbergh/extralibs
endef
endif

$(eval $(generic-package))
