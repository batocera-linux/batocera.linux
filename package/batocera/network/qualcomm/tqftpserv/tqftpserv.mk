################################################################################
#
# tqftpserv
#
################################################################################

TQFTPSERV_VERSION = v1.1.1
TQFTPSERV_SITE = $(call github,linux-msm,tqftpserv,$(TQFTPSERV_VERSION))
TQFTPSERV_LICENSE = BSD-3-Clause license
TQFTPSERV_LICENSE_FILE = LICENSE
TQFTPSERV_DEPENDENCIES = qrtr zstd

ifeq ($(BR2_PACKAGE_SYSTEMD),y)
TQFTPSERV_DEPENDENCIES += systemd
else
TQFTPSERV_CONF_OPTS += -Dsystemd-unit-prefix=/tmp
endif

$(eval $(meson-package))
