################################################################################
#
# MK_ARCADE_JOYSTICK_RPI
#
################################################################################
MK_ARCADE_JOYSTICK_RPI_VERSION = master
MK_ARCADE_JOYSTICK_RPI_SITE = $(call github,digitallumberjack,mk_arcade_joystick_rpi,master)
MK_ARCADE_JOYSTICK_RPI_DEPENDENCIES = linux

define MK_ARCADE_JOYSTICK_RPI_BUILD_CMDS
		$(MAKE) -C $(@D) -f Makefile.cross $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR)
endef

define MK_ARCADE_JOYSTICK_RPI_INSTALL_TARGET_CMDS
	$(MAKE) -C $(@D) -f Makefile.cross $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR) modules_install
endef

$(eval $(generic-package))
