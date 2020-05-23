##########################################################™™######################
#
# SUPERMODEL3
#
################################################################################
SUPERMODEL3_VERSION = 7d805e3ef10daa1530159df2e4723603e8448689
SUPERMODEL3_SITE = $(call github,njz3,model3emu,$(SUPERMODEL3_VERSION))
# install in staging for debugging (gdb)
SUPERMODEL3_INSTALL_STAGING=YES

define SUPERMODEL3_BUILD_CMDS
	$(SED) "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+CC =+CC ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+CXX =+CXX ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+LD =+LD ?=+g" $(@D)/Makefiles/Makefile.UNIX
	CXX="$(TARGET_CXX)" \
	CC="$(TARGET_CC)" \
	LD="$(TARGET_CC)" \
	$(MAKE) -C $(@D)/ -f Makefiles/Makefile.UNIX
endef

define SUPERMODEL3_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bin/supermodel \
	$(TARGET_DIR)/usr/bin/supermodel
endef

define SUPERMODEL3_INSTALL_STAGING_CMDS
	$(INSTALL) -D $(@D)/bin/supermodel \
	$(STAGING_DIR)/usr/bin/supermodel
endef

$(eval $(generic-package))
