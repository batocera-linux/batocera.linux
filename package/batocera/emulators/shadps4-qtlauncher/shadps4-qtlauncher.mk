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
# shadps4-qtlauncher
#
################################################################################

SHADPS4_QTLAUNCHER_VERSION = shadPS4QtLauncher-2026-06-20-cead95c781211cccc83fa54e7ec5f180938fcd14
SHADPS4_QTLAUNCHER_SITE = https://github.com/shadps4-emu/shadps4-qtlauncher
SHADPS4_QTLAUNCHER_SITE_METHOD = git
SHADPS4_QTLAUNCHER_GIT_SUBMODULES = YES
SHADPS4_QTLAUNCHER_LICENSE = GPL-2.0+
SHADPS4_QTLAUNCHER_LICENSE_FILES = LICENSE
SHADPS4_QTLAUNCHER_SUPPORTS_IN_SOURCE_BUILD = NO

SHADPS4_QTLAUNCHER_DEPENDENCIES = openssl qt6base qt6multimedia qt6tools sdl3 vulkan-headers

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
SHADPS4_QTLAUNCHER_DEPENDENCIES += qt6wayland
endif

SHADPS4_QTLAUNCHER_CMAKE_BACKEND = ninja

SHADPS4_QTLAUNCHER_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
SHADPS4_QTLAUNCHER_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
SHADPS4_QTLAUNCHER_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++"
SHADPS4_QTLAUNCHER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SHADPS4_QTLAUNCHER_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
SHADPS4_QTLAUNCHER_CONF_OPTS += -DENABLE_UPDATER=OFF

define SHADPS4_QTLAUNCHER_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    $(INSTALL) -m 0755 $(@D)/buildroot-build/shadPS4QtLauncher $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
