################################################################################
#
# ROCKCHIP RGA2
#
################################################################################

ROCKCHIP_RGA2_VERSION = mainline
ROCKCHIP_RGA2_SITE =  $(call github,rtissera,rga2,$(ROCKCHIP_RGA2_VERSION))
ROCKCHIP_RGA2_INSTALL_STAGING = YES
ROCKCHIP_RGA2_DEPENDENCIES = libdrm

ROCKCHIP_RGA2_MODULE_MAKE_OPTS = \
        CONFIG_ROCKCHIP_RGA2=m \
        USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
                -Wno-error"

define ROCKCHIP_RGA2_MAKE_SUBDIR
        (cd $(@D); ln -s . rga2)
endef

ROCKCHIP_RGA2_PRE_CONFIGURE_HOOKS += ROCKCHIP_RGA2_MAKE_SUBDIR

$(eval $(kernel-module))
$(eval $(generic-package))
