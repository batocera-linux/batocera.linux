################################################################################
#
# python-binho-host-adapter
#
################################################################################

PYTHON_BINHO_HOST_ADAPTER_VERSION = 0.1.6
PYTHON_BINHO_HOST_ADAPTER_SOURCE = binho-host-adapter-$(PYTHON_BINHO_HOST_ADAPTER_VERSION).tar.gz
PYTHON_BINHO_HOST_ADAPTER_SITE = https://files.pythonhosted.org/packages/68/36/29b7b896e83e195fac6d64ccff95c0f24a18ee86e7437a22e60e0331d90a
PYTHON_BINHO_HOST_ADAPTER_SETUP_TYPE = setuptools

PYTHON_BINHO_HOST_ADAPTER_DEPENDENCIES = python-serial

$(eval $(python-package))
