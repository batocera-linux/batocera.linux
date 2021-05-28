################################################################################
#
# TSUGARU
#
################################################################################
# Version.: Commits on May 19, 2021
TSUGARU_VERSION = v20210519
TSUGARU_SITE = $(call github,captainys,TOWNSEMU,$(TSUGARU_VERSION))
TSUGARU_DEPENDENCIES = libglu
TSUGARU_LICENSE = GPLv2

# CMakeLists.txt in src subfolder
TSUGARU_SUBDIR = src

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
TSUGARU_SUPPORTS_IN_SOURCE_BUILD = NO

TSUGARU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
TSUGARU_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

TSUGARU_CONF_ENV += LDFLAGS=-lpthread

define TSUGARU_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin

        $(INSTALL) -D $(@D)/src/buildroot-build/main_cui/Tsugaru_CUI \
                $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
