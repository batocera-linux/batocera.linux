################################################################################
#
# ffmpeg-python
#
################################################################################

FFMPEG_PYTHON_VERSION = df129c7ba30aaa9ffffb81a48f53aa7253b0b4e6
FFMPEG_PYTHON_SITE = $(call github,kkroening,ffmpeg-python,$(FFMPEG_PYTHON_VERSION))
FFMPEG_PYTHON_SETUP_TYPE = setuptools
FFMPEG_PYTHON_LICENSE_FILES = LICENSE

FFMPEG_PYTHON_DEPENDENCIES = python-future

$(eval $(python-package))
