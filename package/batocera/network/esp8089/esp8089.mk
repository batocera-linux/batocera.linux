################################################################################
#
# ESP8089
#
################################################################################
# Version.: Commits on Aug 4, 2023
ESP8089_VERSION = 6afa97bc839ce1a67700c38b01f0f6f3168ec2a4
ESP8089_SITE = $(call github,al177,esp8089,$(ESP8089_VERSION))
ESP8089_LICENSE = GPL-2.0
ESP8089_LICENSE_FILES = LICENSE

ESP8089_MODULE_MAKE_OPTS = \
	CONFIG_ESP8089=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
