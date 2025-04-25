################################################################################
#
# db9_gpio_rpi
#
################################################################################
# Version: Commits on Oct 10, 2024
DB9_GPIO_RPI_VERSION = 4318dc14dab75ba0d150bbedf1a8155ef3284669
DB9_GPIO_RPI_SITE = $(call github,marqs85,db9_gpio_rpi,$(DB9_GPIO_RPI_VERSION))

# Needed because can't pass cflags to cc
define DB9_GPIO_RPI_RPI2_HOOK
    $(SED) "s/#define BCM2708_PERI_BASE + 0x200000/#define BCM2708_PERI_BASE + 0x3F000000/g" \
        $(@D)/db9_gpio_rpi.c
endef

define DB9_GPIO_RPI_FIX_EXTRACT
    mv $(@D)/db9_gpio_rpi/* $(@D)/
endef

DB9_GPIO_RPI_POST_EXTRACT_HOOKS += DB9_GPIO_RPI_FIX_EXTRACT

ifeq ($(BR2_cortex_a7)$(BR2_cortex_a53),y)
    DB9_GPIO_RPI_PRE_CONFIGURE_HOOKS += DB9_GPIO_RPI_RPI2_HOOK
endif

$(eval $(kernel-module))
$(eval $(generic-package))
