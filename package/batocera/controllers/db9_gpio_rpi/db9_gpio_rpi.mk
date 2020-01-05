################################################################################
#
# DB9_GPIO_RPI
#
################################################################################
DB9_GPIO_RPI_VERSION = c21faee29e42696722a953a8eee9093a223f1408
DB9_GPIO_RPI_SITE = $(call github,marqs85,db9_gpio_rpi,$(DB9_GPIO_RPI_VERSION))
DB9_GPIO_RPI_DEPENDENCIES = linux

# Needed because can't pass cflags to cc
define DB9_GPIO_RPI_RPI2_HOOK
        $(SED) "s/#define BCM2708_PERI_BASE 0x20000000/#define BCM2708_PERI_BASE 0x3F000000/g" $(@D)/db9_gpio_rpi-1.2/db9_gpio_rpi.c
endef

ifeq ($(BR2_cortex_a7),y)
        DB9_GPIO_RPI_PRE_CONFIGURE_HOOKS += DB9_GPIO_RPI_RPI2_HOOK
endif
ifeq ($(BR2_cortex_a53),y)
        DB9_GPIO_RPI_PRE_CONFIGURE_HOOKS += DB9_GPIO_RPI_RPI2_HOOK
endif

define DB9_GPIO_RPI_BUILD_CMDS
        $(MAKE) -C $(@D)/db9_gpio_rpi-1.2 $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR)
endef

define DB9_GPIO_RPI_INSTALL_TARGET_CMDS
        $(MAKE) -C $(@D)/db9_gpio_rpi-1.2 $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR) modules_install
endef

$(eval $(generic-package))
