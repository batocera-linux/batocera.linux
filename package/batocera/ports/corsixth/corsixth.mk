################################################################################
#
# CORSIXTH
#
################################################################################

CORSIXTH_VERSION = v0.67
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES = sdl2 sdl2_image lua luafilesystem lpeg luasocket luasec

$(eval $(cmake-package))
