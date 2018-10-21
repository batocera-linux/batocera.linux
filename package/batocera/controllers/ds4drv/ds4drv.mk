################################################################################
#
# DS4DRV
#
################################################################################
DS4DRV_VERSION = be7327fc3f5abb8717815f2a1a2ad3d335535d8a
DS4DRV_SITE =  $(call github,chrippa,ds4drv,$(DS4DRV_VERSION))
DS4DRV_SETUP_TYPE = setuptools

DS4DRV_POST_INSTALL_TARGET_HOOKS += DS4DRV_INSTALL_SERVICE

define DS4DRV_INSTALL_SERVICE
  cp package/batocera/controllers/ds4drv/S31ds4drv $(TARGET_DIR)/etc/init.d/S31ds4drv
endef


$(eval $(python-package))
