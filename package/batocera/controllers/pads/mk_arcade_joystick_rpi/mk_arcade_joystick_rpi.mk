################################################################################
#
# mk_arcade_joystick_rpi
#
################################################################################
# Version: 0.1.8 Commits on Jul 18, 2026
MK_ARCADE_JOYSTICK_RPI_VERSION = 9e008672f281027a1f7816877e955b0c3a39a6d1
MK_ARCADE_JOYSTICK_RPI_SITE = \
    $(call github,batocera-linux,mk_arcade_joystick_rpi,$(MK_ARCADE_JOYSTICK_RPI_VERSION))
MK_ARCADE_JOYSTICK_RPI_DEPENDENCIES = linux

define MK_ARCADE_JOYSTICK_RPI_MAKE_HOOK
	cp $(@D)/Makefile.cross $(@D)/Makefile
endef
MK_ARCADE_JOYSTICK_RPI_PRE_BUILD_HOOKS += MK_ARCADE_JOYSTICK_RPI_MAKE_HOOK

$(eval $(kernel-module))
$(eval $(generic-package))
