################################################################################
#
# keros-leds
#
################################################################################
KEROS_LEDS_VERSION = 2f66450cad94ff435dc2ce5185ff16f9ca31f5d2
KEROS_LEDS_SITE = \
    $(call github,ImanolBarba,keros-leds,$(KEROS_LEDS_VERSION))
KEROS_LEDS_LICENSE = GPL-3.0
KEROS_LEDS_LICENSE_FILES = LICENSE

KEROS_LEDS_MODULE_MAKE_OPTS = \
        CONFIG_KEROS_LEDS=m \
        USER_EXTRA_CFLAGS="-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
