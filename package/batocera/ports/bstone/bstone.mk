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
# bstone
#
################################################################################

BSTONE_VERSION = v1.2.15
BSTONE_SITE = $(call github,bibendovsky,bstone,$(BSTONE_VERSION))
BSTONE_SUPPORTS_IN_SOURCE_BUILD = NO
BSTONE_LICENSE = GPLv2 & MIT
BSTONE_LICENSE_FILE = LICENSE.txt

BSTONE_DEPENDENCIES = openal sdl2

BSTONE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
BSTONE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
BSTONE_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"

define BSTONE_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/bstone/bstone.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

BSTONE_POST_INSTALL_TARGET_HOOKS += BSTONE_EVMAPY

$(eval $(cmake-package))
