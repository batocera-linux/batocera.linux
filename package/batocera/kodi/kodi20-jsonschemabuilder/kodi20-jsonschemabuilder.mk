################################################################################
#
# kodi20-jsonschemabuilder
#
################################################################################

# Not possible to directly refer to kodi variables, because of
# first/second expansion trickery...
KODI20_JSONSCHEMABUILDER_VERSION = 20.2-Nexus
KODI20_JSONSCHEMABUILDER_SITE = $(call github,xbmc,xbmc,$(KODI20_JSONSCHEMABUILDER_VERSION))
KODI20_JSONSCHEMABUILDER_SOURCE = kodi-$(KODI20_JSONSCHEMABUILDER_VERSION).tar.gz
KODI20_JSONSCHEMABUILDER_DL_SUBDIR = kodi
KODI20_JSONSCHEMABUILDER_LICENSE = GPL-2.0
KODI20_JSONSCHEMABUILDER_LICENSE_FILES = LICENSE.md
HOST_KODI20_JSONSCHEMABUILDER_SUBDIR = tools/depends/native/JsonSchemaBuilder

HOST_KODI20_JSONSCHEMABUILDER_CONF_OPTS = \
	-DCMAKE_MODULE_PATH=$(@D)/project/cmake/modules

define HOST_KODI20_JSONSCHEMABUILDER_INSTALL_CMDS
	$(INSTALL) -m 755 -D \
		$(@D)/tools/depends/native/JsonSchemaBuilder/JsonSchemaBuilder \
		$(HOST_DIR)/bin/JsonSchemaBuilder
endef

$(eval $(host-cmake-package))
