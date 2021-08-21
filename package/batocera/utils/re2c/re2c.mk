################################################################################
#
# re2c
#
################################################################################

RE2C_VERSION = 2.2
RE2C_SITE =  $(call github,skvadrik,re2c,$(RE2C_VERSION))

define RE2C_AUTOGEN
    cd $(@D); ./autogen.sh
endef

RE2C_PRE_CONFIGURE_HOOKS += RE2C_AUTOGEN
HOST_RE2C_PRE_CONFIGURE_HOOKS += RE2C_AUTOGEN

$(eval $(autotools-package))
$(eval $(host-autotools-package))
