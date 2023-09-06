################################################################################
#
# EKA2L1
#
################################################################################
# Dirty version and repo while fixing gcc13 and upstreaming
EKA2L1_VERSION = 42c21bebee8bd25f856e7407ea712ba5f160833e
EKA2L1_SITE = https://github.com/rtissera/EKA2L1.git
EKA2L1_SITE_METHOD=git
EKA2L1_GIT_SUBMODULES=YES
EKA2L1_LICENSE = GPLv2
EKA2L1_DEPENDENCIES = qt6base qt6multimedia

EKA2L1_SUPPORTS_IN_SOURCE_BUILD = NO

EKA2L1_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
EKA2L1_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_ENABLE_SCRIPTING_ABILITY=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_BUILD_TOOLS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_BUILD_TESTS=OFF
#EKA2L1_CONF_OPTS += -DBUILD_STATIC_LIBS=OFF

define EKA2L1_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/eka2l1
    $(TARGET_STRIP) $(@D)/buildroot-build/bin/eka2l1_qt
    cp -R $(@D)/buildroot-build/bin/* \
                $(TARGET_DIR)/usr/eka2l1/
endef


$(eval $(cmake-package))
