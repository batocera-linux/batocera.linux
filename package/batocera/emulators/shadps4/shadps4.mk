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

SHADPS4_VERSION = v.0.15.0
SHADPS4_SITE = https://github.com/shadps4-emu/shadPS4
SHADPS4_SITE_METHOD = git
SHADPS4_EMULATOR_INFO = shadps4.emulator.yml
SHADPS4_GIT_SUBMODULES = YES
SHADPS4_LICENSE = GPLv2
SHADPS4_LICENSE_FILE = LICENSE
SHADPS4_SUPPORTS_IN_SOURCE_BUILD = NO

SHADPS4_DEPENDENCIES += alsa-lib pulseaudio openal openssl libzlib
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

# Dear_ImGui_FontEmbed is a build-time code generator. When cross-compiling
# (e.g. aarch64 host -> x86_64 target) the binary built with the target
# toolchain cannot be executed on the build host, so pre-build it with the
# host compiler and tell CMake to import it (see 0001-imgui-renderer-*.patch).
define SHADPS4_BUILD_HOST_FONTEMBED
	$(HOSTCXX) -O2 -o $(@D)/host-dear-imgui-fontembed \
		$(@D)/externals/dear_imgui/misc/fonts/binary_to_compressed_c.cpp
endef
SHADPS4_PRE_CONFIGURE_HOOKS += SHADPS4_BUILD_HOST_FONTEMBED

SHADPS4_CONF_OPTS += -DDear_ImGui_FontEmbed_EXECUTABLE=$(BUILD_DIR)/shadps4-$(SHADPS4_VERSION)/host-dear-imgui-fontembed

$(eval $(cmake-package))
$(eval $(emulator-info-package))
