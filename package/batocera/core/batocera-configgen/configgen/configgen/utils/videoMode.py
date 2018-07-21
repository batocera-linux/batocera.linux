#!/usr/bin/env python
import os
import sys
import recalboxFiles
import re
from settings.unixSettings import UnixSettings
import time
import subprocess
import json
import eslog

# Set a specific video mode
def changeResolution(videomode):
    eslog.log("videomode: " + videomode)
    if videomode != 'default':
        cmd = createVideoModeLine(videomode)
        if cmd is not None:
            eslog.log("setVideoMode(" + videomode + "): " + cmd)
            os.system(cmd)
            time.sleep(0.5) # let time for the video to change the resolution (the commands returns before it's really done ;-(
    
def createVideoModeLine(videoMode):
    # pattern (CEA|DMT) [0-9]{1,2} HDMI
    if re.match("^(CEA|DMT) [0-9]{1,2}( HDMI)?$", videoMode):
        return "tvservice -e '{}'".format(videoMode)
    if re.match("^hdmi_cvt [\d\s]{10,20}$", videoMode):
        return "vcgencmd {} && tvservice -e 'DMT 87'".format(videoMode)
    if re.match("^hdmi_timings [\d\s]{48,58}$", videoMode):
        return "vcgencmd {} && tvservice -e 'DMT 87'".format(videoMode)
    return None

# Switch to prefered mode
def resetResolution():
    recalSettings = UnixSettings(recalboxFiles.recalboxConf)
    esVideoMode = recalSettings.load('system.es.videomode')
    if esVideoMode is None:
        cmd = "tvservice -p"
        eslog.log("resetting video mode: " + cmd)
        os.system(cmd)
    else:
        setVideoMode(esVideoMode)

def getCurrentResolution():
	proc = subprocess.Popen(["tvservice.current"], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	tvmodes = json.loads(out)

	for tvmode in tvmodes:
	    return { "width": tvmode["width"], "height": tvmode["height"] }

        raise Exception("No current resolution found")
