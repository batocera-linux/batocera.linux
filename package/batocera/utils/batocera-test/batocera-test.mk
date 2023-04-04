################################################################################
#
# batocera-test
#
################################################################################
BATOCERA_TEST_VERSION = 1
BATOCERA_TEST_LICENSE = GPL
BATOCERA_TEST_SOURCE=
BATOCERA_TEST_DEPENDENCIES = python-requests

define BATOCERA_TEST_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-test/batocera-test $(TARGET_DIR)/usr/bin/batocera-test
endef

$(eval $(generic-package))
