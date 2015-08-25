################################################################################
#
# VIRTUALGAMEPADS
#
################################################################################
VIRTUALGAMEPADS_VERSION = f2c36d9bc668580173dc690baab329fd91a05183
VIRTUALGAMEPADS_SITE = $(call github,miroof,node-virtual-gamepads,$(VIRTUALGAMEPADS_VERSION))
VIRTUALGAMEPADS_DEPENDENCIES = nodejs

NPM = $(TARGET_CONFIGURE_OPTS) \
	LD="$(TARGET_CXX)" \
	npm_config_arch=arm \
	npm_config_target_arch=arm \
	npm_config_build_from_source=true \
	npm_config_nodedir=$(BUILD_DIR)/nodejs-0.12.7 \
	$(HOST_DIR)/usr/bin/npm


define VIRTUALGAMEPADS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/node-virtual-gamepads
	cp -r $(@D)/* \
		$(TARGET_DIR)/usr/node-virtual-gamepads

	cd $(TARGET_DIR)/usr/node-virtual-gamepads && mkdir -p node_modules && \
		$(NPM) install \

endef


define VIRTUALGAMEPADS_INSTALL_INIT_SYSV
	$(INSTALL) -m 0755 -D package/virtualgamepads/S92virtualgamepads $(TARGET_DIR)/etc/init.d/S92virtualgamepads
endef
$(eval $(generic-package))
