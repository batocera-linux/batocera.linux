################################################################################
#
# date
#
################################################################################

DATE_VERSION = v3.0.4
DATE_SITE = $(call github,HowardHinnant,date,$(DATE_VERSION))
DATE_LICENSE = MIT license
DATE_LICENSE_FILES = LICENSE.txt
DATE_SUPPORTS_IN_SOURCE_BUILD = NO
DATE_INSTALL_STAGING = YES
DATE_INSTALL_TARGET = NO

DATE_DEPENDENCIES = 

DATE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
