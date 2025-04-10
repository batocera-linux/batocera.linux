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
# Version: Commits on Mar 10, 2025
OPENJK_VERSION = 5878f620f6dabb6573595470627ab2e31cb46b67
OPENJK_SITE = https://github.com/JACoders/OpenJK
OPENJK_SITE_METHOD = git
OPENJK_SUPPORTS_IN_SOURCE_BUILD = NO
OPENJK_LICENSE = GPL-2.0 license
OPENJK_LICENSE_FILE = LICENSE.txt

OPENJK_DEPENDENCIES += host-libjpeg libjpeg-bato libpng sdl2 zlib

OPENJK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENJK_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENJK_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"
# Jedi Outcast
OPENJK_CONF_OPTS += -DBuildJK2SPEngine=ON
OPENJK_CONF_OPTS += -DBuildJK2SPGame=ON
OPENJK_CONF_OPTS += -DBuildJK2SPRdVanilla=ON

define OPENJK_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/openjk/openjk.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

OPENJK_POST_INSTALL_TARGET_HOOKS += OPENJK_EVMAPY

$(eval $(cmake-package))
