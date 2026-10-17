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
# ymir
#
################################################################################

YMIR_VERSION = v0.4.0
YMIR_SITE = https://github.com/StrikerX3/Ymir
YMIR_SITE_METHOD = git
YMIR_GIT_SUBMODULES = YES
YMIR_LICENSE = GPLv2
YMIR_LICENSE_FILE = LICENSE
YMIR_EMULATOR_INFO = ymir.emulator.yml
YMIR_DEPENDENCIES += catch2 cereal cxxopts date fmt host-clang host-pkgconf
YMIR_DEPENDENCIES += json-for-modern-cpp libcurl lz4 miniz nghttp3 ngtcp2 openssl
YMIR_DEPENDENCIES += rtmidi sdl3 semver stb tomlplusplus xxhash zlib zstd

YMIR_SUPPORTS_IN_SOURCE_BUILD = NO

YMIR_CMAKE_BACKEND = ninja
# Use clang
YMIR_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
YMIR_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
YMIR_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lstdc++ -lm"

YMIR_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
YMIR_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
YMIR_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
YMIR_CONF_OPTS += -DYmir_DEV_BUILD=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_IMGUI_DEMO=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_SANDBOX=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_TESTS=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_YMDASM=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_IPO=ON
YMIR_CONF_OPTS += -DYmir_ENABLE_UPDATE_CHECKS=OFF
# the vulkan backend is unimplemented but becomes the default when found, and needs dxc
YMIR_CONF_OPTS += -DCMAKE_DISABLE_FIND_PACKAGE_Vulkan=ON

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
    YMIR_CONF_OPTS += -DYmir_AVX2=ON
else
    YMIR_CONF_OPTS += -DYmir_AVX2=OFF
endif

define YMIR_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/buildroot-build/apps/ymir-sdl3/ymir-sdl3-* \
	    $(TARGET_DIR)/usr/bin/ymir
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
