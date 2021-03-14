################################################################################
#
# sdl12-compat
#
################################################################################
# Version.: Commits on Mar 14, 2021
SDL12_COMPAT_VERSION = a719acd09903a3917340f93ce223a28961d27652
SDL12_COMPAT_SITE =  $(call github,libsdl-org,sdl12-compat,$(SDL12_COMPAT_VERSION))
SDL12_COMPAT_LICENSE = MIT

SDL12_COMPAT_DEPENDENCIES = sdl2 sdl

define SDL12_COMPAT_INSTALL_TARGET_CMDS
	cp $(@D)/libSDL* $(TARGET_DIR)/usr/lib/
endef


$(eval $(cmake-package))
