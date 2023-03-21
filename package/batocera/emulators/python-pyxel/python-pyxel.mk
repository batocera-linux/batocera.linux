################################################################################
#
# python-pyxel
#
################################################################################

# Last commit:Feb 5, 2023
PYTHON_PYXEL_VERSION = v1.9.12
PYTHON_PYXEL_SITE =  $(call github,kitao,pyxel,$(PYTHON_PYXEL_VERSION))
PYTHON_PYXEL_SETUP_TYPE = setuptools
PYTHON_PYXEL_LICENSE = MIT
PYTHON_PYXEL_SETUP_TYPE = pep517
PYTHON_PYXEL_ENV = CARGO_HOME=$(@D)

PYTHON_PYXEL_DEPENDENCIES = host-rustc host-rust-bin sdl2 host-python-maturin

define PYTHON_PYXEL_REMOVE_PREVIOUS
	rm -rf $(TARGET_DIR)/usr/bin/pyxel
endef

define PYTHON_PYXEL_SAMPLE_AND_KEYS
   rm -rf $(TARGET_DIR)/usr/lib/python*/site-packages/pyxel/examples
   cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/python-pyxel/pyxel.keys $(TARGET_DIR)/usr/share/evmapy/
endef

PYTHON_PYXEL_PRE_INSTALL_TARGET_HOOKS += PYTHON_PYXEL_REMOVE_PREVIOUS

PYTHON_PYXEL_POST_INSTALL_TARGET_HOOKS += PYTHON_PYXEL_SAMPLE_AND_KEYS

$(eval $(python-package))
