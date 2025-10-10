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
# shadps4
#
################################################################################

SHADPS4_VERSION = SHAD_PS4_PLUS_0_11_0
SHADPS4_SITE = https://github.com/AzaharPlus/shadPS4Plus
SHADPS4_SITE_METHOD = git
SHADPS4_GIT_SUBMODULES = YES
SHADPS4_LICENSE = GPLv2
SHADPS4_LICENSE_FILE = LICENSE

SHADPS4_SUPPORTS_IN_SOURCE_BUILD = NO

SHADPS4_DEPENDENCIES += host-shadps4 alsa-lib pulseaudio openal openssl libzlib
SHADPS4_DEPENDENCIES += libedit udev libevdev jack2 qt6base qt6svg qt6tools
SHADPS4_DEPENDENCIES += qt6multimedia vulkan-headers vulkan-loader
SHADPS4_DEPENDENCIES += vulkan-validationlayers sdl3

SHADPS4_CMAKE_BACKEND = ninja
# Use clang for performance
SHADPS4_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
SHADPS4_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
SHADPS4_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++"

SHADPS4_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SHADPS4_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
SHADPS4_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SHADPS4_CONF_OPTS += -DENABLE_QT_GUI=ON
SHADPS4_CONF_OPTS += -DENABLE_DISCORD_RPC=OFF
SHADPS4_CONF_OPTS += -DENABLE_UPDATER=OFF
SHADPS4_CONF_OPTS += -DVMA_ENABLE_INSTALL=ON

define SHADPS4_INSTALL_TARGET_CMDS
	 mkdir -p $(TARGET_DIR)/usr/bin/shadps4
	 $(INSTALL) -m 0755 $(@D)/buildroot-build/shadps4 $(TARGET_DIR)/usr/bin/shadps4/
	 cp -pr $(@D)/buildroot-build/translations $(TARGET_DIR)/usr/bin/shadps4/
endef

define HOST_SHADPS4_BUILD_CMDS
	$(CXX) $(@D)/externals/dear_imgui/misc/fonts/binary_to_compressed_c.cpp -o \
	    $(@D)/shadps4_Dear_ImGui_FontEmbed
endef

define HOST_SHADPS4_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/shadps4_Dear_ImGui_FontEmbed \
	    $(HOST_DIR)/usr/bin/shadps4_Dear_ImGui_FontEmbed
endef

$(eval $(cmake-package))
$(eval $(host-generic-package))
