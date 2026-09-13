################################################################################
#
# asio
#
################################################################################

ASIO_VERSION = asio-1-38-2
ASIO_SITE = $(call github,chriskohlhoff,asio,$(ASIO_VERSION))
ASIO_LICENSE = BSL-1.0
ASIO_LICENSE_FILES = LICENSE_1_0.txt

# asio is a header-only library, it only makes sense
# to have it installed into the staging directory.
ASIO_INSTALL_STAGING = YES
ASIO_INSTALL_TARGET = NO

define ASIO_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/include
	$(INSTALL) -m 0644 $(@D)/include/asio.hpp $(STAGING_DIR)/usr/include/asio.hpp
	cp -a $(@D)/include/asio $(STAGING_DIR)/usr/include/
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/libraries/asio/asio.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/asio.pc
endef

$(eval $(generic-package))
