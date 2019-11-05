################################################################################
#
# fmt
#
################################################################################
# Batocera: Newer versions of Citra-emu Requires Version 6.0.0
FMT_VERSION = 6.0.0
FMT_SITE = $(call github,fmtlib,fmt,$(FMT_VERSION))
FMT_LICENSE = BSD-2-Clause
FMT_LICENSE_FILES = LICENSE.rst
FMT_INSTALL_STAGING = YES

FMT_CONF_OPTS = \
	-DHAVE_OPEN=ON \
	-DFMT_INSTALL=ON \
	-DFMT_TEST=OFF

$(eval $(cmake-package))
