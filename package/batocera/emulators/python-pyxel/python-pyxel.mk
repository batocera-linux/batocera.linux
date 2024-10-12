################################################################################
#
# python-pyxel
#
################################################################################

PYTHON_PYXEL_VERSION = v2.2.4
PYTHON_PYXEL_SITE =  $(call github,kitao,pyxel,$(PYTHON_PYXEL_VERSION))
PYTHON_PYXEL_SETUP_TYPE = setuptools
PYTHON_PYXEL_LICENSE = MIT
PYTHON_PYXEL_SETUP_TYPE = maturin
PYTHON_PYXEL_CARGO_MANIFEST_PATH = crates/pyxel-extension/Cargo.toml
PYTHON_PYXEL_DEPENDENCIES = host-rust-bin sdl2

PYTHON_PYXEL_SUBDIR = python

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	PYXEL_CARGO_TARGET=x86_64-unknown-linux-gnu
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	PYXEL_CARGO_TARGET=aarch64-unknown-linux-gnu
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	PYXEL_CARGO_TARGET=aarch64-unknown-linux-gnu
endif

PYTHON_PYXEL_ENV = CARGO_HOME=$(@D) TARGET=$(PYXEL_CARGO_TARGET)

define PYTHON_PYXEL_REMOVE_PREVIOUS
	rm -rf $(TARGET_DIR)/usr/bin/pyxel
endef

define PYTHON_PYXEL_SAMPLE_AND_KEYS
	cp -rf $(@D)/python/pyxel $(TARGET_DIR)/usr/lib/python*/site-packages/
	rm -rf $(TARGET_DIR)/usr/lib/python*/site-packages/pyxel/examples
	cd $(TARGET_DIR)/usr/lib/python*/site-packages/pyxel && ln -sf ../pyxel_extension .
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/python-pyxel/pyxel.keys \
	    $(TARGET_DIR)/usr/share/evmapy/
endef

define PYTHON_PYXEL_FIX_BUILD
    $(SED) "s+-I/usr/include+-I$(STAGING_DIR)/usr/include/SDL2+g" \
	    $(@D)/rust/pyxel-platform/build.rs
endef

PYTHON_PYXEL_PRE_CONFIGURE_HOOKS += PYTHON_PYXEL_FIX_BUILD

PYTHON_PYXEL_PRE_INSTALL_TARGET_HOOKS += PYTHON_PYXEL_REMOVE_PREVIOUS

PYTHON_PYXEL_POST_INSTALL_TARGET_HOOKS += PYTHON_PYXEL_SAMPLE_AND_KEYS

$(eval $(python-package))

# python-package sets this to run cargo after download, but we want to let maturin do that
PYTHON_PYXEL_DOWNLOAD_POST_PROCESS =
