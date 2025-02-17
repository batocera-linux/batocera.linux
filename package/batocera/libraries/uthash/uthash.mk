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
# uthash
#
################################################################################

UTHASH_VERSION = v2.3.0
UTHASH_SITE = $(call github,troydhanson,uthash,$(UTHASH_VERSION))
UTHASH_LICENSE = Custom
UTHASH_LICENSE_FILE = LICENSE
UTHASH_INSTALL_STAGING = YES
UTHASH_INSTALL_TARGET = NO

define UTHASH_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/include
	cp -pr $(@D)/src/ut*.h $(STAGING_DIR)/usr/include/
endef

$(eval $(generic-package))
