################################################################################
#
# MK_ARCADE_JOYSTICK_RPI
#
################################################################################
# Version: 1.7.0 Commits on May 08, 2020
MK_ARCADE_JOYSTICK_RPI_VERSION = 910dd090459b14d7d1cf186a3dadfd4ff3ec877b
MK_ARCADE_JOYSTICK_RPI_SITE = $(call github,batocera-linux,mk_arcade_joystick_rpi,$(MK_ARCADE_JOYSTICK_RPI_VERSION))
MK_ARCADE_JOYSTICK_RPI_DEPENDENCIES = linux

define MK_ARCADE_JOYSTICK_RPI_MAKE_HOOK
	cp $(@D)/Makefile.cross $(@D)/Makefile
endef
MK_ARCADE_JOYSTICK_RPI_PRE_BUILD_HOOKS += MK_ARCADE_JOYSTICK_RPI_MAKE_HOOK

define MK_ARCADE_JOYSTICK_RPI_BUILD_CMDS
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR)
endef

define MK_ARCADE_JOYSTICK_RPI_INSTALL_TARGET_CMDS
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR) modules_install
endef

$(eval $(generic-package))
