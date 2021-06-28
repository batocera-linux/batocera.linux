################################################################################
#
# RetroFE frontend
#
################################################################################
# Version.: Commits on Jun 06, 2021
RETROFE_VERSION = 9597bdc49a3d5bc71d6bee19b32c10874208bc3d
RETROFE_SITE = https://github.com/phulshof/RetroFE
RETROFE_SITE_METHOD=git
RETROFE_LICENSE = GPLv3
RETROFE_DEPENDENCIES = sdl2 gstreamer1 gst1-plugins-base

RETROFE_SUBDIR = RetroFE/Source
#RETROFE_CONF_OPTS = 
#-DBUILD_SHARED_LIBS=OFF

define RETROFE_INSTALL_TARGET_CMDS
	cd $(@D) && $(HOST_DIR)/bin/python $(@D)/Scripts/Package.py --os=linux --build=full
	mkdir -p $(TARGET_DIR)/opt/retrolx/RetroFE
	cp -R $(@D)/Artifacts/linux/RetroFE/* $(TARGET_DIR)/opt/retrolx/RetroFE/
endef

$(eval $(cmake-package))
