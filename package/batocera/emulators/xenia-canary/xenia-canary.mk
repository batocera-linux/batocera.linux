################################################################################
#
# xenia-canary
#
################################################################################

XENIA_CANARY_SOURCE = xenia_canary.zip
XENIA_CANARY_VERSION = 8678bec
XENIA_CANARY_SITE = https://github.com/xenia-canary/xenia-canary/releases/download/$(XENIA_CANARY_VERSION)
XENIA_CANARY_LICENSE = BSD
XENIA_CANARY_LICENSE_FILE = LICENSE

XENIA_CANARY_DEPENDENCIES = python-toml

# ugly hack becuase the is no version in the source file
define XENIA_CANARY_CLEAR_DL
    if [ -f "$(DL_DIR)/$(XENIA_CANARY_DL_SUBDIR)/$(XENIA_CANARY_SOURCE)" ]; then \
        rm $(DL_DIR)/$(XENIA_CANARY_DL_SUBDIR)/$(XENIA_CANARY_SOURCE); \
    fi
endef

define XENIA_CANARY_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && $(UNZIP) -d $(@D) $(DL_DIR)/$(XENIA_CANARY_DL_SUBDIR)/$(XENIA_CANARY_SOURCE)
endef

define XENIA_CANARY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr
	rsync -av --exclude=".*" $(@D)/ $(TARGET_DIR)/usr/xenia-canary/
endef

define XENIA_CANARY_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/xenia-canary/xbox360.xenia-canary.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

XENIA_CANARY_PRE_DOWNLOAD_HOOKS = XENIA_CANARY_CLEAR_DL
XENIA_CANARY_POST_INSTALL_TARGET_HOOKS = XENIA_CANARY_POST_PROCESS

$(eval $(generic-package))
