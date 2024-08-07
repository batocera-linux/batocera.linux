################################################################################
#
# python-proxy-tools
#
################################################################################
# Version.: Commits on Apr 2+, 2024
PYTHON_PROXY_TOOLS_VERSION = db43f1e35d4f90a65c5a4d56d9e9af88212ec6e6
PYTHON_PROXY_TOOLS_SITE = $(call github,jtushman,proxy_tools,$(PYTHON_PROXY_TOOLS_VERSION))
PYTHON_PROXY_TOOLS_LICENSE = BSD
PYTHON_PROXY_TOOLS_SETUP_TYPE = setuptools

$(eval $(python-package))
