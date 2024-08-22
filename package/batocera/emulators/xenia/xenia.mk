################################################################################
#
# xenia
#
################################################################################

XENIA_SOURCE = xenia_master.zip
XENIA_VERSION = v1.0.2817-master
XENIA_SITE = \
    https://github.com/xenia-project/release-builds-windows/releases/download/$(XENIA_VERSION)
XENIA_LICENSE = BSD
XENIA_LICENSE_FILE = LICENSE

XENIA_DEPENDENCIES = python-toml

# ugly hack becuase the is no version in the source file
define XENIA_CLEAR_DL
    if [ -f "$(DL_DIR)/$(XENIA_DL_SUBDIR)/$(XENIA_SOURCE)" ]; then \
        rm $(DL_DIR)/$(XENIA_DL_SUBDIR)/$(XENIA_SOURCE); \
    fi
endef

define XENIA_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && $(UNZIP) -d $(@D) \
	    $(DL_DIR)/$(XENIA_DL_SUBDIR)/$(XENIA_SOURCE)
endef

define XENIA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr
	rsync -av --exclude=".*" $(@D)/ $(TARGET_DIR)/usr/xenia/
endef

define XENIA_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/xenia/xbox360.xenia.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

XENIA_PRE_DOWNLOAD_HOOKS = XENIA_CLEAR_DL
XENIA_POST_INSTALL_TARGET_HOOKS = XENIA_POST_PROCESS

$(eval $(generic-package))
