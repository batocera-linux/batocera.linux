################################################################################
#
# cs16-client
#
################################################################################

# Version: Commits on Nov 17, 2026
CS16_CLIENT_VERSION = ba5549fe32ce0fd94630a582401fc5b2c76f3f23
CS16_CLIENT_SITE = https://github.com/FWGS/cs16-client.git
CS16_CLIENT_SITE_METHOD = git
CS16_CLIENT_GIT_SUBMODULES = YES
CS16_CLIENT_LICENSE = GPL-2.0+, MIT (ReGameDLL_CS)
CS16_CLIENT_LICENSE_FILES = LICENSE 3rdparty/ReGameDLL_CS/LICENSE
CS16_CLIENT_DEPENDENCIES = host-python3 freetype

define CS16_CLIENT_INSTALL_TARGET_CMDS
	$(BR2_CMAKE) --install $(CS16_CLIENT_BUILDDIR) --prefix $(@D)/bato-install
	mkdir -p $(TARGET_DIR)/usr/lib/xash3d/hlsdk/cstrike $(TARGET_DIR)/usr/share/xash3d/cstrike
	cp -r $(@D)/bato-install/cstrike/cl_dlls $(@D)/bato-install/cstrike/dlls \
	    $(TARGET_DIR)/usr/lib/xash3d/hlsdk/cstrike/
	$(INSTALL) -m 0644 -D $(@D)/bato-install/cstrike/extras.pk3 \
	    $(TARGET_DIR)/usr/share/xash3d/cstrike/extras.pk3
endef

$(eval $(cmake-package))
