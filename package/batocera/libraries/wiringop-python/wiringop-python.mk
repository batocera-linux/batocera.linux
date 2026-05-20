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
# wiringop-python
#
################################################################################
# Version: Commits on Jan 30, 2026
WIRINGOP_PYTHON_VERSION = cde245b3183c3abe48194180b2d2203da08225ee
WIRINGOP_PYTHON_SITE = https://github.com/orangepi-xunlong/wiringOP-Python.git
WIRINGOP_PYTHON_SITE_METHOD = git
WIRINGOP_PYTHON_GIT_SUBMODULES = YES
WIRINGOP_PYTHON_SETUP_TYPE = setuptools
WIRINGOP_PYTHON_LICENSE = GPLv3
WIRINGOP_PYTHON_LICENSE_FILES = LICENSE.txt

WIRINGOP_PYTHON_DEPENDENCIES = host-swig libxcrypt

# Add the flag to ignore implicit function declaration errors
WIRINGOP_PYTHON_ENV = \
	CFLAGS="$(TARGET_CFLAGS) -Wno-error=implicit-function-declaration"

define WIRINGOP_PYTHON_BINDINGS
	cd $(@D) ; \
	$(HOST_DIR)/bin/python3 generate-bindings.py > $(@D)/bindings.i
endef

WIRINGOP_PYTHON_PRE_BUILD_HOOKS = WIRINGOP_PYTHON_BINDINGS

$(eval $(python-package))