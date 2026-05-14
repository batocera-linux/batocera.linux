################################################################################
#
# xxd
#
################################################################################

XXD_VERSION = 084dc9dec6b6a6d048934916aa9a539d49ba898d
XXD_SITE =  $(call github,ConorOG,xxd,$(XXD_VERSION))

define HOST_XXD_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D) CC="$(HOSTCC)" CFLAGS="$(HOST_CFLAGS) -std=gnu89"
endef

define HOST_XXD_INSTALL_CMDS
	$(INSTALL) -D $(@D)/xxd $(HOST_DIR)/usr/bin/xxd
endef

$(eval $(host-generic-package))
