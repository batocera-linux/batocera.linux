################################################################################
#
# Attract-Mode frontend
#
################################################################################
# Version.: Commits on Mar 27, 2021
ATTRACTMODE_VERSION = 75ab7ed04a565760bbacffd339f6cfc87ea97acc
ATTRACTMODE_SITE = https://github.com/mickelson/attract
ATTRACTMODE_SITE_METHOD=git
ATTRACTMODE_LICENSE = GPLv3
ATTRACTMODE_DEPENDENCIES = sfml

# Attract-Mode depends on SFML2
# SFML2 heavily depends on X11, so no luck outside x86_64

#ATTRACTMODE_CONF_OPTS = 

define ATTRACTMODE_BUILD_CMDS
	cd $(@D) && make
endef

define ATTRACTMODE_INSTALL_TARGET_CMDS
	cd $(@D) && make install 
endef

$(eval $(generic-package))
