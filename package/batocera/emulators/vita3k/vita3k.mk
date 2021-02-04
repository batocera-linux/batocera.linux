################################################################################
#
# VITA3K
#
################################################################################
# Version.: Relase on December 25th, 2020
VITA3K_VERSION = 64d30bf7a56a600320247cf305f0c67273b0c190
VITA3K_SITE = https://github.com/vita3k/vita3k.git
VITA3K_SITE_METHOD=git
VITA3K_GIT_SUBMODULES=YES
VITA3K_LICENSE = GPLv2
VITA3K_DEPENDENCIES = sdl2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
VITA3K_SUPPORTS_IN_SOURCE_BUILD = NO

VITA3K_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VITA3K_CONF_OPTS += -DUSE_DISCORD_RICH_PRESENCE=OFF
VITA3K_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

VITA3K_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
