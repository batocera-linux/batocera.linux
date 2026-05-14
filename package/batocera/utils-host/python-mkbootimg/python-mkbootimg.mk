################################################################################
#
# python-mkbootimg
#
################################################################################

PYTHON_MKBOOTIMG_DEPENDENCIES += python

PYTHON_MKBOOTIMG_SITE = \
https://android.googlesource.com/platform/system/tools/mkbootimg/+/refs/heads/main/mkbootimg.py?format=TEXT

define HOST_PYTHON_MKBOOTIMG_INSTALL_CMDS
	wget --tries=10 --retry-connrefused --waitretry=5 --timeout=30 \
		${PYTHON_MKBOOTIMG_SITE} -O ${@D}/mkbootimg.b64 && \
		base64 -d ${@D}/mkbootimg.b64 > ${@D}/mkbootimg.py ; \
	$(INSTALL) -D -m 0755 ${@D}/mkbootimg.py $(HOST_DIR)/usr/bin/mkbootimg.py ;
endef

$(eval $(host-generic-package))
