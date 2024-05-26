################################################################################
#
# xa
#
################################################################################

XA_VERSION = 2.4.1
XA_SOURCE=xa-$(XA_VERSION).tar.gz
XA_SITE = https://www.floodgap.com/retrotech/xa/dists

define HOST_XA_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D) -f Makefile
endef

define HOST_XA_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/xa $(HOST_DIR)/usr/bin/xa ;
endef

$(eval $(host-generic-package))
