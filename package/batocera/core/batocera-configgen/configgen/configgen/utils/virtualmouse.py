from __future__ import annotations

import logging
import subprocess
import pyudev
import subprocess
import time

eslog = logging.getLogger(__name__)

def generateVirtualMouse(emulator: str):

    if emulator is None or emulator not in [ 'libretro' ]:
        return None

    eslog.info(f"Create virtual mouse")

    create_cmd = ["/usr/bin/evsieve"]
    context = pyudev.Context()
     # touchpad need abs to rel convertion, available in master branch only currentl
     #--abs-to-rel rel:x abs:x:0~255  speed=1   #available in master branch only currently

#    for device in context.list_devices(subsystem='input').match_property('ID_INPUT_TOUCHPAD', '1'):
#         if device.sys_name.startswith('event'):
#             create_cmd.extend(['--input', '/dev/input/' + device.sys_name, '--abs-to-rel','rel:x','abs:x:0~255','speed=1'])

    for device in context.list_devices(subsystem='input').match_property('ID_INPUT_MOUSE', '1'):
        if device.sys_name.startswith('event'):
            create_cmd.extend(['--input', '/dev/input/' + device.sys_name])

    create_cmd.extend(['--output', 'rel:x', 'rel:y', 'btn:left', 'btn:middle', 'btn:right', 'name=Virtual_Multi_Mouse', 'create-link=/dev/input/Virtual_Multi_Mouse'])
    proc = subprocess.Popen(create_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(1)
    return proc


def destroyVirtualMouse(proc: subprocess.Popen[bytes]) -> None:
    eslog.info(f"killing virtual mouse process {proc.pid}")
    proc.kill()
    out, err = proc.communicate()

