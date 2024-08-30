################################################################################
#
# cpuinfo
#
################################################################################
# Version: Commits on Aug 31, 2024
CPUINFO_VERSION = fa1c679da8d19e1d87f20175ae1ec10995cd3dd3
CPUINFO_SITE = https://github.com/pytorch/cpuinfo.git
CPUINFO_SITE_METHOD = git
CPUINFO_INSTALL_STAGING = YES
CPUINFO_LICENSE = BSD2
CPUINFO_LICENSE_FILE = LICENSE

CPUINFO_DEPENDENCIES = host-libcurl

CPUINFO_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
CPUINFO_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

CPUINFO_CONF_ENV += LDFLAGS=-lpthread

# workaround certificate errors
define CPUINFO_DLD_DEPENDENCIES
	mkdir -p $(@D)/deps/googlebenchmark-download/googlebenchmark-prefix/src
	mkdir -p $(@D)/deps/googletest-download/googletest-prefix/src
	$(HOST_DIR)/bin/curl -L http://github.com/google/benchmark/archive/v1.6.1.zip \
        -o $(@D)/deps/googlebenchmark-download/googlebenchmark-prefix/src/v1.6.1.zip
	$(HOST_DIR)/bin/curl -L https://github.com/google/googletest/archive/release-1.11.0.zip \
	    -o $(@D)/deps/googletest-download/googletest-prefix/src/release-1.11.0.zip
endef

CPUINFO_PRE_CONFIGURE_HOOKS += CPUINFO_DLD_DEPENDENCIES

$(eval $(cmake-package))
