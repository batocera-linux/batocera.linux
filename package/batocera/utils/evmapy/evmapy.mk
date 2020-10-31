################################################################################
#
# EVMAPY
#
################################################################################
EVMAPY_VERSION = bd65338c236cd30b4f2d7835733ea5d6b108b75d
EVMAPY_SITE =  $(call github,kempniu,evmapy,$(EVMAPY_VERSION))
EVMAPY_SETUP_TYPE = setuptools

define EVMAPY_FIXCHARS
        sed -i -e s+"Michał Kępień"+"Michal Kepien"+ $(@D)/*.py $(@D)/evmapy/*.py
endef
EVMAPY_PRE_CONFIGURE_HOOKS += EVMAPY_FIXCHARS

define EVMAPY_INSTALL_SCRIPTS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/evmapy/batocera-evmapy $(TARGET_DIR)/usr/bin
endef

EVMAPY_POST_INSTALL_TARGET_HOOKS = EVMAPY_INSTALL_SCRIPTS

$(eval $(python-package))
