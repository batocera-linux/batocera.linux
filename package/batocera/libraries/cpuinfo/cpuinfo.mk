################################################################################
#
# cpuinfo
#
################################################################################
# Version: Commits on Jul 10, 2024
CPUINFO_VERSION = ca678952a9a8eaa6de112d154e8e104b22f9ab3f
CPUINFO_SITE = https://github.com/pytorch/cpuinfo.git
CPUINFO_SITE_METHOD = git
CPUINFO_SUPPORTS_IN_SOURCE_BUILD = NO
CPUINFO_INSTALL_STAGING = YES
CPUINFO_LICENSE = BSD2
CPUINFO_LICENSE_FILE = LICENSE

CPUINFO_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
CPUINFO_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

CPUINFO_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
