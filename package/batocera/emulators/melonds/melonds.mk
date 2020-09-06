################################################################################
#
# MELONDS
#
################################################################################
# Version.: Relase on September 5th, 2020
MELONDS_VERSION = 0.9
MELONDS_SITE = https://github.com/Arisotura/melonDS.git
MELONDS_SITE_METHOD=git
MELONDS_GIT_SUBMODULES=YES
MELONDS_LICENSE = GPLv2
MELONDS_DEPENDENCIES = sdl2 qt5base slirp

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
MELONDS_SUPPORTS_IN_SOURCE_BUILD = NO

MELONDS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

MELONDS_CONF_ENV += LDFLAGS=-lpthread

define MELONDS_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/buildroot-build/melonDS \
		$(TARGET_DIR)/usr/bin/

endef

$(eval $(cmake-package))
