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
# Version: Commits on Mar 13, 2025
WIRINGOP_PYTHON_VERSION = 152a8c14a2273bfc5aeed3ed3f36d41aef002b45
WIRINGOP_PYTHON_SITE = https://github.com/orangepi-xunlong/wiringOP-Python.git
WIRINGOP_PYTHON_SITE_METHOD = git
WIRINGOP_PYTHON_GIT_SUBMODULES = YES
WIRINGOP_PYTHON_SETUP_TYPE = setuptools
WIRINGOP_PYTHON_LICENSE = GPLv3
WIRINGOP_PYTHON_LICENSE_FILES = LICENSE.txt

WIRINGOP_PYTHON_DEPENDENCIES = host-swig libxcrypt

define WIRINGOP_PYTHON_BINDINGS
	cd $(@D) ; \
	$(HOST_DIR)/bin/python3 generate-bindings.py > $(@D)/bindings.i
endef

WIRINGOP_PYTHON_PRE_BUILD_HOOKS = WIRINGOP_PYTHON_BINDINGS

$(eval $(python-package))
