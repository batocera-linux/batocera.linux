################################################################################
#
# PYTHON_PYQT5_SIP
#
################################################################################
PYTHON_PYQT5_SIP_VERSION = 12.11.0
PYTHON_PYQT5_SIP_SOURCE = PyQt5_sip-$(PYTHON_PYQT5_SIP_VERSION).tar.gz
PYTHON_PYQT5_SIP_SITE = https://files.pythonhosted.org/packages/39/5f/fd9384fdcb9cd0388088899c110838007f49f5da1dd1ef6749bfb728a5da

PYTHON_PYQT5_SIP_SETUP_TYPE = setuptools

$(eval $(python-package))
