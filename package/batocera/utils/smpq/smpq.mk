################################################################################
#
# smpq
#
################################################################################

SMPQ_VERSION = 1.6
SMPQ_SOURCE = smpq_$(SMPQ_VERSION).orig.tar.gz
SMPQ_SITE = https://launchpad.net/smpq/trunk/$(SMPQ_VERSION)/+download
SMPQ_LICENSE = GPL-3.0+
SMPQ_LICENSE_FILES = LICENSE
SMPQ_DEPENDENCIES = stormlib
HOST_SMPQ_DEPENDENCIES = host-stormlib
SMPQ_CONF_OPTS += -DWITH_KDE=OFF
HOST_SMPQ_CONF_OPTS += -DWITH_KDE=OFF
SMPQ_INSTALL_STAGING = YES

$(eval $(cmake-package))
$(eval $(host-cmake-package))
