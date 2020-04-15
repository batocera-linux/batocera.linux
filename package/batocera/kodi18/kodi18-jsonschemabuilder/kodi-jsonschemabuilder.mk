################################################################################
#
# kodi-jsonschemabuilder
#
################################################################################

# Not possible to directly refer to kodi18 variables, because of
# first/second expansion trickery...
KODI18_JSONSCHEMABUILDER_VERSION = 18.6-Leia
KODI18_JSONSCHEMABUILDER_SITE = $(call github,xbmc,xbmc,$(KODI18_JSONSCHEMABUILDER_VERSION))
KODI18_JSONSCHEMABUILDER_SOURCE = kodi18-$(KODI18_JSONSCHEMABUILDER_VERSION).tar.gz
KODI18_JSONSCHEMABUILDER_DL_SUBDIR = kodi18
KODI18_JSONSCHEMABUILDER_LICENSE = GPL-2.0
KODI18_JSONSCHEMABUILDER_LICENSE_FILES = LICENSE.md
HOST_KODI18_JSONSCHEMABUILDER_SUBDIR = tools/depends/native/JsonSchemaBuilder

HOST_KODI18_JSONSCHEMABUILDER_CONF_OPTS = \
	-DCMAKE_MODULE_PATH=$(@D)/project/cmake/modules

define HOST_KODI18_JSONSCHEMABUILDER_INSTALL_CMDS
	$(INSTALL) -m 755 -D \
		$(@D)/tools/depends/native/JsonSchemaBuilder/JsonSchemaBuilder \
		$(HOST_DIR)/bin/JsonSchemaBuilder
endef

$(eval $(host-cmake-package))
