################################################################################
#
# RyzenAdj
#
################################################################################

RYZENADJ_VERSION = 7aeb2f4869ee52ac161ee4cb4871e29113487885
RYZENADJ_SITE = $(call github,FlyGoat,RyzenAdj,$(RYZENADJ_VERSION))
RYZENADJ_LICENSE = GPLv2
RYZENADJ_DEPENDENCIES = pciutils libpciaccess

RYZENADJ_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RYZENADJ_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
RYZENADJ_CONF_OPTS += -DARCHITECTURE_x86_64=ON

define RYZENADJ_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/ryzenadj $(TARGET_DIR)/usr/bin/ryzenadj
	$(INSTALL) -D $(@D)/libryzenadj.so $(TARGET_DIR)/usr/lib/libryzenadj.so
endef

$(eval $(cmake-package))
