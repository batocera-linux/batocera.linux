################################################################################
#
# pm-utils
#
################################################################################

PM_UTILS_VERSION = 1.4.1
PM_UTILS_SITE = http://pm-utils.freedesktop.org/releases
PM_UTILS_SOURCE = pm-utils-$(PM_UTILS_VERSION).tar.gz

$(eval $(autotools-package))
