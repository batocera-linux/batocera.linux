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
# Version: Commits on May 13, 2026
OPENJK_VERSION = 8cce3ea23125f56200b553cd0b149af617adf397
OPENJK_SITE = https://github.com/JACoders/OpenJK
OPENJK_SITE_METHOD = git
OPENJK_SUPPORTS_IN_SOURCE_BUILD = NO
OPENJK_LICENSE = GPL-2.0 license
OPENJK_LICENSE_FILE = LICENSE.txt
OPENJK_EMULATOR_INFO = openjk.emulator.yml

OPENJK_DEPENDENCIES += libjpeg-bato libpng sdl2 zlib

OPENJK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENJK_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENJK_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"
# Jedi Outcast
OPENJK_CONF_OPTS += -DBuildJK2SPEngine=ON
OPENJK_CONF_OPTS += -DBuildJK2SPGame=ON
OPENJK_CONF_OPTS += -DBuildJK2SPRdVanilla=ON

# compact_glsl is a build-time code generator (it embeds .glsl shader files
# into a C++ source file). When cross-compiling, the binary built with the
# target toolchain cannot be executed on the build host, so pre-build it
# with the host compiler and tell CMake to import it via the cache variable
# added in 001-cross-compile.patch.
OPENJK_COMPACT_GLSL_BIN = $(@D)/host-compact_glsl
OPENJK_COMPACT_GLSL_SRCS = \
	$(@D)/codemp/rd-rend2/glsl/compact.cpp \
	$(@D)/codemp/rd-rend2/tr_allocator.cpp \
	$(@D)/codemp/rd-rend2/tr_glsl_parse.cpp

define OPENJK_BUILD_HOST_COMPACT_GLSL
	$(HOSTCXX) -O2 -std=c++11 -DGLSL_BUILDTOOL -DNOMINMAX \
		-DARCH_STRING='"host"' \
		-I$(@D)/codemp -I$(@D)/codemp/rd-rend2 -I$(@D)/shared \
		-I$(@D)/lib/gsl-lite/include \
		-o $(OPENJK_COMPACT_GLSL_BIN) $(OPENJK_COMPACT_GLSL_SRCS)
endef
OPENJK_PRE_CONFIGURE_HOOKS += OPENJK_BUILD_HOST_COMPACT_GLSL

OPENJK_CONF_OPTS += -Dcompact_glsl_EXECUTABLE=$(BUILD_DIR)/openjk-$(OPENJK_VERSION)/host-compact_glsl

define OPENJK_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/openjk/openjk.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

OPENJK_POST_INSTALL_TARGET_HOOKS += OPENJK_EVMAPY

$(eval $(cmake-package))
$(eval $(emulator-info-package))
