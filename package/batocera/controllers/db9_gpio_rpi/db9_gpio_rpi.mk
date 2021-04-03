################################################################################
#
# DB9_GPIO_RPI
#
################################################################################
# Version.: Commits on Feb 1, 2021
DB9_GPIO_RPI_VERSION = a3c16921a812ec2cf24a043a184cf445813bac08
DB9_GPIO_RPI_SITE = $(call github,marqs85,db9_gpio_rpi,$(DB9_GPIO_RPI_VERSION))

# Needed because can't pass cflags to cc
define DB9_GPIO_RPI_RPI2_HOOK
        $(SED) "s/#define BCM2708_PERI_BASE 0x20000000/#define BCM2708_PERI_BASE 0x3F000000/g" $(@D)/db9_gpio_rpi.c
endef

define DB9_GPIO_RPI_FIX_EXTRACT
	mv $(@D)/db9_gpio_rpi-1.2/* $(@D)/
endef
DB9_GPIO_RPI_POST_EXTRACT_HOOKS += DB9_GPIO_RPI_FIX_EXTRACT

ifeq ($(BR2_cortex_a7),y)
        DB9_GPIO_RPI_PRE_CONFIGURE_HOOKS += DB9_GPIO_RPI_RPI2_HOOK
endif
ifeq ($(BR2_cortex_a53),y)
        DB9_GPIO_RPI_PRE_CONFIGURE_HOOKS += DB9_GPIO_RPI_RPI2_HOOK
endif

$(eval $(kernel-module))
$(eval $(generic-package))
