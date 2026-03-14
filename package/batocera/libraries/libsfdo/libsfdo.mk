################################################################################
#
# libsfdo
#
################################################################################

LIBSFDO_VERSION = v0.1.3
LIBSFDO_SITE = $(call github,jlindgren90,libsfdo,$(LIBSFDO_VERSION))
LIBSFDO_LICENSE = BSD-2-Clause
LIBSFDO_LICENSE_FILES = LICENSE
LIBSFDO_INSTALL_STAGING = YES

LIBSFDO_CONF_OPTS = \
	-Dexamples=false \
	-Dtests=false

$(eval $(meson-package))
