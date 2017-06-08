################################################################################
#
# kodi-jsonschemabuilder
#
################################################################################

# Not possible to directly refer to kodi variables, because of
# first/second expansion trickery...
KODI_JSONSCHEMABUILDER_VERSION = 17.3-Krypton
KODI_JSONSCHEMABUILDER_SITE = $(call github,xbmc,xbmc,$(KODI_JSONSCHEMABUILDER_VERSION))
KODI_JSONSCHEMABUILDER_SOURCE = kodi-$(KODI_JSONSCHEMABUILDER_VERSION).tar.gz
KODI_JSONSCHEMABUILDER_LICENSE = GPL-2.0
KODI_JSONSCHEMABUILDER_LICENSE_FILES = LICENSE.GPL
HOST_KODI_JSONSCHEMABUILDER_SUBDIR = tools/depends/native/JsonSchemaBuilder

HOST_KODI_JSONSCHEMABUILDER_CONF_OPTS = \
	-DCMAKE_MODULE_PATH=$(@D)/project/cmake/modules

define HOST_KODI_JSONSCHEMABUILDER_INSTALL_CMDS
	$(INSTALL) -m 755 -D \
		$(@D)/tools/depends/native/JsonSchemaBuilder/JsonSchemaBuilder \
		$(HOST_DIR)/usr/bin/JsonSchemaBuilder
endef

$(eval $(host-cmake-package))
