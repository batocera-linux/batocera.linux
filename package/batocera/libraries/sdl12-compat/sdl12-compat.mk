################################################################################
#
# sdl12-compat
#
################################################################################
# Version.: Commits on Jul 27th, 2023
SDL12_COMPAT_VERSION = f94a1ec0069266e40843138d0c5dd2fc6d43734c
SDL12_COMPAT_SITE =  https://github.com/libsdl-org/sdl12-compat
SDL12_COMPAT_SITE_METHOD =  git
SDL12_COMPAT_LICENSE = LGPLv3
SDL12_COMPAT_INSTALL_STAGING = YES

# Disable tests
SDL12_COMPAT_CONF_OPTS += -DSDL12TESTS=OFF

SDL12_COMPAT_DEPENDENCIES += sdl2

$(eval $(cmake-package))
