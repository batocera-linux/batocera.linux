################################################################################
#
# influxdb
#
################################################################################

INFLUXDB_VERSION = 2.7.6
INFLUXDB_SITE = https://dl.influxdata.com/influxdb/releases
INFLUXDB_LICENSE = Apache-2.0, MIT
INFLUXDB_LICENSE_FILES = LICENSE-APACHE, LICENSE-MIT

ifeq ($(BR2_aarch64),y)
    INFLUXDB_SOURCE = influxdb2-$(INFLUXDB_VERSION)_linux_arm64.tar.gz  
endif

ifeq ($(BR2_x86_64),y)
    INFLUXDB_SOURCE = influxdb2-$(INFLUXDB_VERSION)_linux_amd64.tar.gz
endif

define INFLUXDB_INSTALL_TARGET_CMDS
    cp -f $(@D)/usr/bin/influxd $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
