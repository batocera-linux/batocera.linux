################################################################################
#
# GAMECON_GPIO_RPI
#
################################################################################
GAMECON_GPIO_RPI_VERSION = d70ac2459443f2bd96e8d99bf5dd5b84658ffe77
GAMECON_GPIO_RPI_SITE = $(call github,marqs85,gamecon_gpio_rpi,$(GAMECON_GPIO_RPI_VERSION))

define GAMECON_GPIO_RPI_FIX_EXTRACT
	mv $(@D)/gamecon_gpio_rpi-1.4/* $(@D)/
endef
GAMECON_GPIO_RPI_POST_EXTRACT_HOOKS += GAMECON_GPIO_RPI_FIX_EXTRACT

# Needed because can't pass cflags to cc
define GAMECON_GPIO_RPI_RPI2_HOOK
        $(SED) "s/BCM2708_PERI_BASE + 0x200000/BCM2708_PERI_BASE + 0x3F000000/g" $(@D)/gamecon_gpio_rpi.c
endef

ifeq ($(BR2_cortex_a7),y)
        GAMECON_GPIO_RPI_PRE_CONFIGURE_HOOKS += GAMECON_GPIO_RPI_RPI2_HOOK
endif
ifeq ($(BR2_cortex_a53),y)
        GAMECON_GPIO_RPI_PRE_CONFIGURE_HOOKS += GAMECON_GPIO_RPI_RPI2_HOOK
endif

$(eval $(kernel-module))
$(eval $(generic-package))
