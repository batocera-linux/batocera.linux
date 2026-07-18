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
#################################################################################
#
# trx
#
################################################################################

TRX_VERSION = trx-1.9.2
TRX_SITE = $(call github,LostArtefacts,TRX,$(TRX_VERSION))
TRX_LICENSE = GPL-3.0 license
TRX_LICENSE_FILES = COPYING.md
TRX_SUPPORTS_IN_SOURCE_BUILD = NO
TRX_EMULATOR_INFO = trx.emulator.yml
# meson.build in src subfolder
TRX_SUBDIR = src

TRX_DEPENDENCIES = ffmpeg libglew pcre2 sdl2 uthash lua

TRX_CONF_OPTS = -Dstaticdeps=false

# Use install target commands to get all files & dirs
define TRX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/trx
	cp -f $(@D)/src/buildroot-build/TRX $(TARGET_DIR)/usr/bin/trx/
	cp -rf $(@D)/data/trx/ship/* $(TARGET_DIR)/usr/bin/trx/
endef

$(eval $(meson-package))
$(eval $(emulator-info-package))
