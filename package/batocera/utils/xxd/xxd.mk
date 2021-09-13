################################################################################
#
# xxd
#
################################################################################

XXD_VERSION = 084dc9dec6b6a6d048934916aa9a539d49ba898d
XXD_SITE =  $(call github,ConorOG,xxd,$(XXD_VERSION))

define HOST_XXD_BUILD_CMDS
	$(MAKE) -C $(@D)
endef

define HOST_XXD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/xxd $(HOST_DIR)/usr/bin/xxd
endef

$(eval $(host-generic-package))
