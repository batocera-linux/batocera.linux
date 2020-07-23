################################################################################
#
# CATCH2
#
################################################################################
# Version.: Commits on Jul 08, 2020
CATCH2_VERSION = v2.13.0
CATCH2_SITE = https://github.com/catchorg/Catch2.git
CATCH2_SITE_METHOD=git
CATCH2_GIT_SUBMODULES=YES
CATCH2_LICENSE = BSL-1.0
CATCH2_DEPENDENCIES =

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CATCH2_SUPPORTS_IN_SOURCE_BUILD = NO

CATCH2_CONF_OPTS += -DBUILD_TESTING=OFF -DCMAKE_INSTALL_PREFIX="$(STAGING_DIR)/usr"

define CATCH2_INSTALL_TARGET_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/cmake/Catch2
	$(MAKE) -C $(@D)/buildroot-build install
endef

$(eval $(cmake-package))
