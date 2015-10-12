################################################################################
#
# python-autobreadcrumbs
#
################################################################################

PYTHON_AUTOBREADCRUMBS_VERSION = 1.1
PYTHON_AUTOBREADCRUMBS_SOURCE = autobreadcrumbs-$(PYTHON_AUTOBREADCRUMBS_VERSION).tar.gz
# The official Django site has an unpractical URL
# https://pypi.python.org/packages/source/a/autobreadcrumbs/autobreadcrumbs-1.1.tar.gz#md5=7d56efba990b9d1637df60b5a17a4586
PYTHON_AUTOBREADCRUMBS_SETUP_TYPE = setuptools
PYTHON_AUTOBREADCRUMBS_SITE = https://pypi.python.org/packages/source/a/autobreadcrumbs/
PYTHON_AUTOBREADCRUMBS_LICENSE = BSD-3c
PYTHON_AUTOBREADCRUMBS_LICENSE_FILES = LICENSE

$(eval $(python-package))
