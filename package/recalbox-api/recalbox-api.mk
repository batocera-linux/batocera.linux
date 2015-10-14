################################################################################
#
# RECALBOX_API
#
################################################################################
RECALBOX_API_VERSION = 1.0.6
RECALBOX_API_SITE = $(call github,neolao,recalbox-api,$(RECALBOX_API_VERSION))
RECALBOX_API_DEPENDENCIES = nodejs

NPM = $(TARGET_CONFIGURE_OPTS) \
	LD="$(TARGET_CXX)" \
	npm_config_arch=arm \
	npm_config_target_arch=arm \
	npm_config_build_from_source=true \
	npm_config_nodedir=$(BUILD_DIR)/nodejs-0.12.7 \
	$(HOST_DIR)/usr/bin/npm


define RECALBOX_API_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/recalbox-api
	cp -r $(@D)/* \
		$(TARGET_DIR)/usr/recalbox-api

	cd $(TARGET_DIR)/usr/recalbox-api && mkdir -p node_modules && \
		$(NPM) install \

endef


define RECALBOX_API_INSTALL_INIT_SYSV
	#TODO The init script shouldn't start by default
	#$(INSTALL) -m 0755 -D package/RECALBOX_API/S92RECALBOX_API $(TARGET_DIR)/etc/init.d/S92RECALBOX_API
endef
$(eval $(generic-package))
