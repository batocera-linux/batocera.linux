################################################################################
#
# VITA3K
#
################################################################################
# Version.: Commits on May 30 2022
VITA3K_VERSION = 4071eb35c6427252b0217e1db8d2dae657c6b655
VITA3K_SITE = https://github.com/vita3k/vita3k
VITA3K_SITE_METHOD=git
VITA3K_GIT_SUBMODULES=YES
VITA3K_LICENSE = GPLv3
VITA3K_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf zlib libogg libvorbis

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
VITA3K_SUPPORTS_IN_SOURCE_BUILD = NO

VITA3K_CONF_OPTS = -DBUILD_SHARED_LIBS=OFF -DUSE_DISCORD_RICH_PRESENCE=OFF


$(eval $(cmake-package))
