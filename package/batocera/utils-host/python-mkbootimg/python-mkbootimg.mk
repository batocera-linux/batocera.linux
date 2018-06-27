################################################################################
#
# python-mkbootimg
#
################################################################################

PYTHON_MKBOOTIMG_DEPENDENCIES += python

PYTHON_MKBOOTIMG_SITE = https://raw.githubusercontent.com/aosp-mirror/platform_system_core/master/mkbootimg/mkbootimg

define HOST_PYTHON_MKBOOTIMG_INSTALL_CMDS
	wget ${PYTHON_MKBOOTIMG_SITE} -O ${@D}/mkbootimg ; \
	$(INSTALL) -D -m 0755 ${@D}/mkbootimg $(HOST_DIR)/usr/bin/mkbootimg ;
endef

$(eval $(host-generic-package))
