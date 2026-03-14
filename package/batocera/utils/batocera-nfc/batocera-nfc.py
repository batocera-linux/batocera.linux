#!/usr/bin/env python3

import nfc
import ndef
import sys
import argparse
import serial.tools.list_ports
import subprocess
import time
import signal
from pathlib import Path

NFC_WRITE_TAG_PATH = Path("/var/run/batocera-nfc-write-tag")
NFC_WRITE_TIME = 30
NFC_SCRIPTS_SYSTEM_PATH = Path("/usr/share/batocera/scripts")
NFC_SCRIPTS_USER_PATH   = Path("/userdata/system/configs/emulationstation/scripts")
NFC_AVAILABLE           = Path("/var/run/batocera-nfc.running")

def get_any_device(vids_pids):
    device = get_pn532_by_id(vids_pids)
    return device

def get_pn532_by_id(vids_pids):
    target_port = None
    for p in serial.tools.list_ports.comports():
        if p.vid is not None and p.pid is not None:
            strvid = f"{p.vid:04x}"
            strpid = f"{p.pid:04x}"
            if strvid in vids_pids and strpid in vids_pids[strvid]:
                target_port = p.device
                break
    if not target_port:
        return None
    port = target_port.replace("/dev/", "")
    return f"tty:{port}:pn532"

def callScripts(name, game):
    global gdebug

    # if the user directory exists, ignore the system one
    sysdirectory = NFC_SCRIPTS_SYSTEM_PATH / name
    userdirectory = NFC_SCRIPTS_USER_PATH / name
    directory = None
    if userdirectory.exists():
        directory = userdirectory
    elif sysdirectory.exists():
        directory = sysdirectory
    if directory is not None:
        files = [f for f in directory.iterdir() if f.is_file()]
        for script in files:
            if gdebug:
                print("running script " + str(script) + " with '" + game + "'")
            try:
                subprocess.run([script, game])
            except Exception as e:
                print("script " + str(script) + " failed (" + str(e) + ")")
                pass # ignore failing scripts

def on_connect(tag):
    global gdebug, gwrite

    if gdebug:
        print(f"tag : type:{tag.type} uid:{tag.identifier.hex()} present:{tag.is_present}")

    if NFC_WRITE_TAG_PATH.exists() and (time.time() - NFC_WRITE_TAG_PATH.stat().st_mtime) < NFC_WRITE_TIME: # ignore the tag if is has more than Xs
        gwrite = True
        if not tag.ndef.is_writeable:
            print("write only tag.")
            return True
        record = ndef.TextRecord(NFC_WRITE_TAG_PATH.read_text(), "en")
        tag.ndef.records = [record]
        if gdebug:
            print("Written.")
        NFC_WRITE_TAG_PATH.unlink()
        return True # continue to read tags

    # read
    gwrite = False
    if tag.ndef:
        if tag.ndef.records:
            for record in tag.ndef.records:
                callScripts("on-nfc-connect", record.text)
    return True

def on_disconnect(tag):
    global gdebug
    if gdebug:
        print("tag disconnected")
    if not gwrite:
        if tag.ndef:
            if tag.ndef.records:
                for record in tag.ndef.records:
                    callScripts("on-nfc-disconnect", record.text)

def nfc_write(txt):
    global gdebug
    NFC_WRITE_TAG_PATH.write_text(args.write)
    ntime = NFC_WRITE_TIME
    while NFC_WRITE_TAG_PATH.exists() and ntime > 0:
        if gdebug:
            print("waiting a tag (" + str(ntime) + ")")
        time.sleep(1)
        ntime = ntime -1
    if NFC_WRITE_TAG_PATH.exists():
        return False
    return True

def cleanup(signum, frame):
    NFC_AVAILABLE.unlink(missing_ok=True)
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, help="example : tty:USB0:pn532")
parser.add_argument("--write",  type=str, help="string to write")
parser.add_argument("--debug",  action="store_true")
args = parser.parse_args()

gdebug  = args.debug
gwrite  = False # write done on connect

if args.write:
    if nfc_write(args.write):
        exit(0)
    else:
        exit(1)

# device white list
vids_pids = {
    "1a86": {
        "7523": {}
    }
}

if args.device:
    device = args.device
else:
    device = get_any_device(vids_pids)

if device is None:
    print("No device found")
    exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

while True:
    try:
        with nfc.ContactlessFrontend(device) as clf:
            NFC_AVAILABLE.touch()  # declare that reading is available
            clf.connect(rdwr={'on-connect': on_connect, 'on-release': on_disconnect})
            clf.connect(rdwr={'on-connect': on_connect, 'on-release': on_disconnect})
    except Exception as e:
        print("reader failed with (" + str(e) + ")")
    finally:
        NFC_AVAILABLE.unlink(missing_ok=True) # reading is no more available
    time.sleep(3) # avoid looping in case of strange behavior
### end ###
