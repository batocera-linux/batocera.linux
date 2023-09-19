################################################################################
#
# innoextract
#
################################################################################
INNOEXTRACT_VERSION = 1.9
INNOEXTRACT_SITE = $(call github,dscharrer,innoextract,$(INNOEXTRACT_VERSION))
INNOEXTRACT_LICENSE = MIT
INNOEXTRACT_DEPENDENCIES = host-cmake xz boost

INNOEXTRACT_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
