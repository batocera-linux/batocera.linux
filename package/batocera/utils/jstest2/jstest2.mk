################################################################################
#
# jstest2
#
################################################################################

JSTEST2_VERSION = 301a0e8cf3f96de4c5e58d9fe4413e5cd2b4e6d4
JSTEST2_SITE = $(call github,Grumbel,sdl-jstest,$(JSTEST2_VERSION))
JSTEST2_DEPENDENCIES = sdl2

$(eval $(cmake-package))
