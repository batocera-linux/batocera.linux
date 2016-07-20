################################################################################
#
# evwait
#
################################################################################

EVWAIT_VERSION = 242a3a8ced19ff979b215607d316801d2bb15b4b
EVWAIT_SITE = $(call github,nadenislamarre,evwait,$(EVWAIT_VERSION))
EVWAIT_LICENSE = GPLv2+
EVWAIT_LICENSE_FILES = COPYING
EVWAIT_DEPENDENCIES = host-pkgconf
# needed because source package contains no generated files
EVWAIT_AUTORECONF = YES

# asciidoc used to generate manpages, which we don't need, and if it's
# present on the build host, it ends getting called with our host-python
# which doesn't have all the needed modules enabled, breaking the build
EVWAIT_CONF_ENV = ac_cv_path_ASCIIDOC=""

$(eval $(autotools-package))
