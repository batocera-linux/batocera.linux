################################################################################
#
# Roshambo Case
#
################################################################################

ROSHAMBO_CASE_VERSION = 81c04334a3049f301294743e9e15806aa086221a
ROSHAMBO_CASE_SITE = $(call github,mrfixit2001,Rock64-R64.GPIO,$(ROSHAMBO_CASE_VERSION))
ROSHAMBO_CASE_LICENSE = GPL-3.0+, others
ROSHAMBO_CASE_DEPENDENCIES = python

define ROSHAMBO_CASE_BUILD_CMDS
	(cd $(@D) && python -m compileall R64)
	(cd $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/roshambo-case && python -m compileall roshambo-case.py)
endef

define ROSHAMBO_CASE_INSTALL_TARGET_CMDS
	install -d -m 755      $(TARGET_DIR)/usr/lib/python2.7/site-packages/R64
	cp -r $(@D)/R64/*      $(TARGET_DIR)/usr/lib/python2.7/site-packages/R64

	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/roshambo-case/S14roshambo       $(TARGET_DIR)/etc/init.d/
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/roshambo-case/roshambo-case.py* $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
