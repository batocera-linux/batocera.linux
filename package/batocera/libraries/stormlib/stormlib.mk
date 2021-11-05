################################################################################
#
# stormlib
#
################################################################################

STORMLIB_VERSION = 5ab093b7a57b8779dff06a08fac19d46c40b3329
STORMLIB_SITE = $(call github,ladislav-zezula,StormLib,$(STORMLIB_VERSION))
STORMLIB_LICENSE = MIT
STORMLIB_LICENSE_FILES = LICENSE
STORMLIB_DEPENDENCIES = zlib bzip2
HOST_STORMLIB_DEPENDENCIES = host-zlib host-bzip2
STORMLIB_INSTALL_STAGING = YES

$(eval $(cmake-package))
$(eval $(host-cmake-package))
