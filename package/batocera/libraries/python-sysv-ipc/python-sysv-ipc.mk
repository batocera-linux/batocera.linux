################################################################################
#
# python-sysv-ipc
#
################################################################################

PYTHON_SYSV_IPC_VERSION = 1.1.0
PYTHON_SYSV_IPC_SOURCE = sysv_ipc-$(PYTHON_SYSV_IPC_VERSION).tar.gz
PYTHON_SYSV_IPC_SITE = https://files.pythonhosted.org/packages/0c/d7/5d2f861155e9749f981e6c58f2a482d3ab458bf8c35ae24d4b4d5899ebf9
PYTHON_SYSV_IPC_SETUP_TYPE = setuptools
PYTHON_SYSV_IPC_LICENSE = BSD
PYTHON_SYSV_IPC_LICENSE_FILES = LICENSE

$(eval $(python-package))
