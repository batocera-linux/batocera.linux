################################################################################
#
# uqm
#
################################################################################

# Version: Commits on Aug 21, 2026
UQM_VERSION = a0d90e239b3a8e3dcb9d732fd76a385aac2593e5
UQM_SITE = https://git.code.sf.net/p/sc2/uqm
UQM_SITE_METHOD = git
UQM_DEPENDENCIES = sdl2 libpng libvorbis libzip
UQM_SUBDIR = sc2
UQM_EMULATOR_INFO = uqm.emulator.yml

define UQM_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/sc2/src/urquan -D $(TARGET_DIR)/usr/bin/urquan
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
