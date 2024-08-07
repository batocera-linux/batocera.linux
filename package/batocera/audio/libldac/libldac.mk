################################################################################
#
# libldac
#
################################################################################
# Version: v2.0.2.3
LIBLDAC_VERSION = af2dd23979453bcd1cad7c4086af5fb421a955c5
LIBLDAC_SITE = https://github.com/EHfive/ldacBT.git
LIBLDAC_SITE_METHOD = git
LIBLDAC_GIT_SUBMODULES = YES
LIBLDAC_LICENSE = Apache-2.0 license
LIBLDAC_LICENSE_FILES = LICENSE
LIBLDAC_INSTALL_STAGING = YES

$(eval $(cmake-package))
