################################################################################
#
# pysdl3
#
################################################################################

PYSDL3_VERSION = v0.9.8b8
PYSDL3_SITE = $(call github,Aermoss,PySDL3,$(PYSDL3_VERSION))
PYSDL3_LICENSE = MIT
PYSDL3_LICENSE_FILES = LICENSE
PYSDL3_SETUP_TYPE = setuptools

HOST_PYSDL3_NEEDS_HOST_PYTHON = python3

PYSDL3_BIN_FOLDER = \
    $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/sdl3/bin

define PYSDL3_CREATE_METADATA_JSON
	mkdir -p $(PYSDL3_BIN_FOLDER)
	( \
		echo '{' ; \
		echo '  "system": "Linux",' ; \
		echo '  "arch": "AMD64",' ; \
		echo '  "target": "$(PYSDL3_VERSION)",' ; \
		echo '  "files": [' ; \
		echo '    "/usr/lib/libSDL3.so",' ; \
		echo '    "/usr/lib/libSDL3_image.so",' ; \
		echo '    "/usr/lib/libSDL3_mixer.so",' ; \
		echo '    "/usr/lib/libSDL3_ttf.so"' ; \
		echo '  ],' ; \
		echo '  "repair": true,' ; \
		echo '  "find": true' ; \
		echo '}' ; \
	) > $(PYSDL3_BIN_FOLDER)/metadata.json
endef

PYSDL3_POST_INSTALL_TARGET_HOOKS += PYSDL3_CREATE_METADATA_JSON

$(eval $(python-package))
