################################################################################
#
# muparser
#
################################################################################

MUPARSER_VERSION = v2.3.2
MUPARSER_SITE = $(call github,beltoforion,muparser,$(MUPARSER_VERSION))
MUPARSER_LICENSE = BSD
MUPARSER_DEPENDENCIES = 

MUPARSER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
MUPARSER_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
MUPARSER_CONF_OPTS += -DARCHITECTURE_x86_64=ON

define MUPARSER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/libmuparser.so.2.3.2 $(TARGET_DIR)/usr/lib/libmuparser.so.2.3.2
	ln -sf /usr/lib/libmuparser.so.2.3.2 $(TARGET_DIR)/usr/lib/libmuparser.so
	ln -sf /usr/lib/libmuparser.so.2.3.2 $(TARGET_DIR)/usr/lib/libmuparser.so.2
endef

$(eval $(cmake-package))
