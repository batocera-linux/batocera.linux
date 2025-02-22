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
# tr1x
#
################################################################################

TR1X_VERSION = tr1-4.8.3
TR1X_SITE = $(call github,LostArtefacts,TRX,$(TR1X_VERSION))
TR1X_LICENSE = GPL-3.0 license
TR1X_LICENSE_FILES = COPYING.md
TR1X_SUPPORTS_IN_SOURCE_BUILD = NO
# meson.build in src/tr1 subfolder
TR1X_SUBDIR = src/tr1

TR1X_DEPENDENCIES = ffmpeg4 libglew pcre2 sdl2 uthash

TR1X_CONF_OPTS = -Dstaticdeps=false

# Use install target commands to get all files & dirs
define TR1X_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/tr1x
	cp -f $(@D)/src/tr1/build/TR1X $(TARGET_DIR)/usr/bin/tr1x/
	cp -rf $(@D)/data/tr1/ship/* $(TARGET_DIR)/usr/bin/tr1x/
endef

$(eval $(meson-package))
