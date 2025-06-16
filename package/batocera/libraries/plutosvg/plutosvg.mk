################################################################################
#
# plutosvg
#
################################################################################

PLUTOSVG_VERSION = v0.0.7
PLUTOSVG_SITE = https://github.com/sammycage/plutosvg
PLUTOSVG_SITE_METHOD = git
PLUTOSVG_GIT_SUBMODULES = YES
PLUTOSVG_LICENSE = MIT License
PLUTOSVG_LICENSE_FILES = LICENSE
PLUTOSVG_DEPENDENCIES = 
PLUTOSVG_SUPPORTS_IN_SOURCE_BUILD = NO

PLUTOSVG_INSTALL_STAGING = YES

PLUTOSVG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
PLUTOSVG_CONF_OPTS += -DPLUTOSVG_BUILD_EXAMPLES=OFF

$(eval $(cmake-package))
