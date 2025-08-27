################################################################################
#
# pysdl2
#
################################################################################

PYSDL2_VERSION = 0.9.17
PYSDL2_SITE = $(call github,py-sdl,py-sdl2,$(PYSDL2_VERSION))
PYSDL2_LICENSE = CC0 Public Domain Dedication
PYSDL2_LICENSE_FILES = doc/copying.rst
PYSDL2_SETUP_TYPE = setuptools

HOST_PYSDL2_NEEDS_HOST_PYTHON = python3

PYSDL2_DEPENDENCIES = host-python-setuptools-scm

$(eval $(python-package))
