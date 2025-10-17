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
# openjk
#
################################################################################
# Version: Commits on Oct 10, 2025
OPENJK_VERSION = d1cb662f07dfa4c1999edfb5c1a86fd1c6285372
OPENJK_SITE = https://github.com/JACoders/OpenJK
OPENJK_SITE_METHOD = git
OPENJK_SUPPORTS_IN_SOURCE_BUILD = NO
OPENJK_LICENSE = GPL-2.0 license
OPENJK_LICENSE_FILE = LICENSE.txt

OPENJK_DEPENDENCIES += host-openjk libjpeg-bato libpng sdl2 zlib

OPENJK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENJK_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENJK_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"
# Jedi Outcast
OPENJK_CONF_OPTS += -DBuildJK2SPEngine=ON
OPENJK_CONF_OPTS += -DBuildJK2SPGame=ON
OPENJK_CONF_OPTS += -DBuildJK2SPRdVanilla=ON

HOST_OPENJK_DEPENDENCIES = mesa3d

HOST_OPENJK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_OPENJK_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
HOST_OPENJK_CONF_OPTS += -DUseInternalSDL2=ON
HOST_OPENJK_CONF_OPTS += -DUseInternalJPEG=ON
HOST_OPENJK_CONF_OPTS += -DUseInternalPNG=ON

HOST_OPENJK_BUILD_OPTS += --target compact_glsl

define OPENJK_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/openjk/openjk.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

define HOST_OPENJK_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(HOST_OPENJK_BUILDDIR)/compact_glsl \
	    $(HOST_DIR)/usr/bin/compact_glsl
endef

OPENJK_POST_INSTALL_TARGET_HOOKS += OPENJK_EVMAPY

$(eval $(cmake-package))
$(eval $(host-cmake-package))
