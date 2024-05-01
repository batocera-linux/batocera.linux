################################################################################
#
# MK_ARCADE_JOYSTICK_RPI
#
################################################################################
# Version: 0.1.8 Commits on Sep 20, 2020
MK_ARCADE_JOYSTICK_RPI_VERSION = e1db04befc729e420d32b62dd14ecff8fb7cedd3
MK_ARCADE_JOYSTICK_RPI_SITE = $(call github,batocera-linux,mk_arcade_joystick_rpi,$(MK_ARCADE_JOYSTICK_RPI_VERSION))
MK_ARCADE_JOYSTICK_RPI_DEPENDENCIES = linux

define MK_ARCADE_JOYSTICK_RPI_MAKE_HOOK
	cp $(@D)/Makefile.cross $(@D)/Makefile
endef
MK_ARCADE_JOYSTICK_RPI_PRE_BUILD_HOOKS += MK_ARCADE_JOYSTICK_RPI_MAKE_HOOK

$(eval $(kernel-module))
$(eval $(generic-package))
