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
# tr2x
#
################################################################################

TR2X_VERSION = tr2-0.9.2
TR2X_SITE = $(call github,LostArtefacts,TRX,$(TR2X_VERSION))
TR2X_LICENSE = GPL-3.0 license
TR2X_LICENSE_FILES = COPYING.md
TR2X_SUPPORTS_IN_SOURCE_BUILD = NO
# meson.build in src/tr2 subfolder
TR2X_SUBDIR = src/tr2

TR2X_DEPENDENCIES = ffmpeg4 libglew pcre2 sdl2 uthash

TR2X_CONF_OPTS = -Dstaticdeps=false

# Use install target commands to get all files & dirs
define TR2X_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/tr2x
	cp -f $(@D)/src/tr2/build/TR2X $(TARGET_DIR)/usr/bin/tr2x/
	cp -rf $(@D)/data/tr2/ship/* $(TARGET_DIR)/usr/bin/tr2x/
endef

$(eval $(meson-package))
