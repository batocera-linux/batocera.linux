################################################################################
#
# Free Heroes (of Might and Magic) 2 engine
#
################################################################################

FHEROES2_VERSION = 1.0.12
FHEROES2_SITE = $(call github,ihhub,fheroes2,$(FHEROES2_VERSION))
FHEROES2_DEPENDENCIES = sdl2 sdl2_image

$(eval $(cmake-package))
