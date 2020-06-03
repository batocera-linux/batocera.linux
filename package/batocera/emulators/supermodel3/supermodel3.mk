##########################################################™™######################
#
# SUPERMODEL3
#
################################################################################
SUPERMODEL3_VERSION = 11dfa544b8b0bf79d3952f955128cec0041482cf
SUPERMODEL3_SITE = $(call github,rtissera,model3emu,$(SUPERMODEL3_VERSION))
# install in staging for debugging (gdb)
SUPERMODEL3_INSTALL_STAGING=YES

define SUPERMODEL3_BUILD_CMDS
	$(SED) "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+CC =+CC ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+CXX =+CXX ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+LD =+LD ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+-march=native+-msse+g" $(@D)/Makefiles/Makefile.inc
	$(SED) "s+OUTFILE = supermodel+OUTFILE = supermodel3+g" $(@D)/Makefiles/Makefile.inc
	CXX="$(TARGET_CXX)" \
	CC="$(TARGET_CC)" \
	LD="$(TARGET_CC)" \
	$(MAKE) -C $(@D)/ -f Makefiles/Makefile.UNIX
endef

define SUPERMODEL3_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bin/supermodel3 \
	$(TARGET_DIR)/usr/bin/supermodel3
endef

define SUPERMODEL3_INSTALL_STAGING_CMDS
	$(INSTALL) -D $(@D)/bin/supermodel3 \
	$(STAGING_DIR)/usr/bin/supermodel3
endef

$(eval $(generic-package))
