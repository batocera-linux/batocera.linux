################################################################################
#
# aml-dtbtools
#
################################################################################


AML_DTBTOOLS_VERSION = master
AML_DTBTOOLS_SITE = $(call github,Wilhansen,aml-dtbtools,$(AML_DTBTOOLS_VERSION))

define HOST_AML_DTBTOOLS_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D) -f Makefile
endef

define HOST_AML_DTBTOOLS_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/dtbTool $(HOST_DIR)/usr/bin/dtbTool ; \
	$(INSTALL) -D -m 0755 $(@D)/dtbSplit $(HOST_DIR)/usr/bin/dtbSplit ;
endef

$(eval $(host-generic-package))
