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
# openjkdf2
#
################################################################################

OPENJKDF2_VERSION = v0.9.8
OPENJKDF2_SITE = https://github.com/shinyquagsire23/OpenJKDF2
OPENJKDF2_SITE_METHOD = git
OPENJKDF2_GIT_SUBMODULES = YES
OPENJKDF2_SUPPORTS_IN_SOURCE_BUILD = NO
OPENJKDF2_LICENSE = GPLv2 & MIT
OPENJKDF2_LICENSE_FILE = LICENSE.txt

OPENJKDF2_DEPENDENCIES += gamenetworkingsockets host-python-cog libcurl libfreeglut
OPENJKDF2_DEPENDENCIES += libglew libgtk3 libpng openal physfs protobuf python3
OPENJKDF2_DEPENDENCIES += sdl2 sdl2_mixer zlib

OPENJKDF2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENJKDF2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENJKDF2_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
OPENJKDF2_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
OPENJKDF2_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++"
OPENJKDF2_CONF_OPTS += -DCMAKE_CXX_FLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include/SDL2 \
                                         -I$(STAGING_DIR)/usr/include/GameNetworkingSockets"
OPENJKDF2_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"
OPENJKDF2_CONF_OPTS += -DPLAT_LINUX_64=ON
# Avoid building libraries set crosscompiling off, although we are...
OPENJKDF2_CONF_OPTS += -DCMAKE_CROSSCOMPILING=NO

define OPENJKDF2_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    cp $(@D)/buildroot-build/openjkdf2 $(TARGET_DIR)/usr/bin/
endef

define OPENJKDF2_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/openjkdf2/openjkdf2.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

OPENJKDF2_POST_INSTALL_TARGET_HOOKS += OPENJKDF2_EVMAPY

$(eval $(cmake-package))
