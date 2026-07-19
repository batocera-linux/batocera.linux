################################################################################
#
# miniz
#
################################################################################

MINIZ_VERSION = 3.1.2
MINIZ_SITE = $(call github,richgel999,miniz,$(MINIZ_VERSION))
MINIZ_LICENSE = MIT
MINIZ_INSTALL_STAGING = YES

$(eval $(cmake-package))
