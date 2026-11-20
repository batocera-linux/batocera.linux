################################################################################
#
# swt6621s
#
################################################################################

# Version: Commits on Nov 12, 2026
SWT6621S_VERSION = e49829a8919391af5d564245b3292544480bbb16
SWT6621S_SITE = $(call github,Novice-PG,swt6621s,$(SWT6621S_VERSION))
SWT6621S_LICENSE = GPL-2.0
SWT6621S_LICENSE_FILES = LICENSE
SWT6621S_DEPENDENCIES = host-perl

SWT6621S_MODULE_SUBDIRS = src
SWT6621S_MODULE_MAKE_OPTS = PERL=$(HOST_DIR)/bin/perl

$(eval $(kernel-module))
$(eval $(generic-package))
