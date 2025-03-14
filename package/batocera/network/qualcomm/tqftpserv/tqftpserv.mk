################################################################################
#
# tqftpserv
#
################################################################################

TQFTPSERV_VERSION = 533779cb8a1843581d5422a7f0aae1a35e6ab956
TQFTPSERV_SITE = $(call github,andersson,tqftpserv,$(TQFTPSERV_VERSION))
TQFTPSERV_LICENSE = BSD-3-Clause license
TQFTPSERV_LICENSE_FILE = LICENSE
TQFTPSERV_DEPENDENCIES = host-qrtr qrtr zstd

$(eval $(meson-package))
