#!/bin/bash

#WDIR=/srv/rhodecode
VIRTUALENV_DIR=/usr/recalbox-manager

source $VIRTUALENV_DIR/bin/activate
$VIRTUALENV_DIR/bin/python $VIRTUALENV_DIR/manage.py runserver 0.0.0.0:80 &

#cd $WDIR
#paster serve production.ini 1> debug.log 2> error.log
