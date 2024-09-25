#!/usr/bin/env python3

import pyudev
import evdev
from evdev import ecodes
import select
import os
import time
import json
import re
import sys
import argparse
import signal

DEVICE_NAME   = "batocera hotkeys"
gcontext_file = "/var/run/hotkeygen.context"
gpid_file     = "/var/run/hotkeygen.pid"
gsystem_dir   = "/usr/share/hotkeygen"
guser_dir     = "/userdata/system/configs/hotkeygen"
gdebug = False
gcontext = {}

ecodesNames = {}
for x in ecodes.ecodes:
    if x[:4] == "KEY_":
        ecodesNames[ecodes.ecodes[x]] = x

knownActions = ["exit", "coin", "menu", "files", "save_state", "restore_state", "next_slot", "previous_slot", "screenshot"]

# default context is for es
def getDefaultContext():
    return {
        "name": "emulationstation",
        "keys": {
            "exit": ecodes.KEY_ESC,
            "menu": ecodes.KEY_SPACE,
            "files": ecodes.KEY_F1
        }
    }

def getContext():
    context_file = gcontext_file
    if os.path.exists(context_file):
        try:
            if gdebug:
                print("using default context {}".format(context_file))
            data = {}
            with open(context_file, 'r') as file:
                data = json.load(file)
                return loadContext(data)
        except Exception as e:
            print("fail to load context file : {}".format(e))
            return {}
    else:
        context = getDefaultContext()
        if gdebug:
            print("using default context")
            printContext(context)
        return context

def loadContext(data):
    if "name" not in data:
        raise Exception("no name section found")
    if "keys" not in data:
        raise Exception("no keys section found")
    context = { "name": data["name"], "keys": {} }
    for k in data["keys"]:
        if k in knownActions:
            if type(data["keys"][k]) is list:
                context["keys"][k] = []
                for x in data["keys"][k]:
                    if x in ecodes.ecodes:
                        context["keys"][k].append(ecodes.ecodes[x])
                    else:
                        raise Exception("invalid key '{}'".format(x))
            else:
                if data["keys"][k] in ecodes.ecodes:
                    context["keys"][k] = ecodes.ecodes[data["keys"][k]]
                else:
                    raise Exception("invalid key '{}'".format(data["keys"][k]))
        else:
            raise Exception("invalid entry '{}'".format(k))
    
    if gdebug:
        printContext(context)
    return context

def saveContext(context, gcontext_file):
    save = { "name": context["name"], "keys": {} }
    for k in context["keys"]:
        if type(context["keys"][k]) is list:
            save["keys"][k] = []
            for x in context["keys"][k]:
                save["keys"][k].append(ecodesNames[x])
        else:
            save["keys"][k] = ecodesNames[context["keys"][k]]

    with open(gcontext_file, "w") as fd:
        json.dump(save, fd, indent=2) 

def printContext(context):
    print("Context [{}]:".format(context["name"]))
    for k in context["keys"]:
        if type(context["keys"][k]) is list:
            str = ""
            for x in context["keys"][k]:
                if str != "":
                    str = str + ", "
                str = str + ecodesNames[x]
            print("  {:-<15}-> [{}]".format(k, str))
        else:
            print("  {:-<15}-> {}".format(k, ecodesNames[context["keys"][k]]))

def getDeviceConfigFilename(device):
    return "{}-{:02x}-{:02x}.mapping".format(re.sub('[^a-zA-Z0-9_]', '', device.name.replace(' ', '_')), device.info.vendor, device.info.product)

def getMappingFullPath(device):
    fullpath = None
    fname = getDeviceConfigFilename(device)
    if gdebug:
        print("...looking for {}, {}".format("{}/{}".format(guser_dir, fname), "{}/{}".format(gsystem_dir, fname)))
    if os.path.exists("{}/{}".format(guser_dir, fname)):
        fullpath = "{}/{}".format(guser_dir, fname)
    elif os.path.exists("{}/{}".format(gsystem_dir, fname)):
        fullpath = "{}/{}".format(gsystem_dir, fname)
    return fullpath

def getMapping(device):
    fullpath = getMappingFullPath(device)

    if fullpath is not None:
        if gdebug:
            print("using mapping {}".format(fullpath))
        with open(fullpath, 'r') as fd:
            data = json.load(fd)
        return loadMapping(data)
    else:
        # default for all inputs
        return {
            ecodes.KEY_EXIT:     "exit",
            ecodes.KEY_EURO:     "coin",
            ecodes.KEY_MENU:     "menu",
            ecodes.KEY_FILE:     "files",
            ecodes.KEY_SAVE:     "save_state",
            ecodes.KEY_SEND:     "restore_state",
            ecodes.KEY_NEXT:     "next_slot",
            ecodes.KEY_PREVIOUS: "previous_slot",
            ecodes.KEY_SCREEN:   "screenshot"
        }

def loadMapping(data):
    try:
        mapping = {}
        for k in data:
            if data[k] in knownActions:
                if k in ecodes.ecodes:
                    mapping[ecodes.ecodes[k]] = data[k]
                else:
                    raise Exception("invalid key '{}'".format(data[k]))
            else:
                raise Exception("invalid entry '{}'".format(data[k]))
        return mapping
    except Exception as e:
        print("fail to load mapping : {}".format(e))
        return {}

def getMappingAssociations(mapping, caps):
    res = {}
    capskeys = {}
    for k in caps[ecodes.EV_KEY]:
        capskeys[k] = True
    for k in mapping:
        if k in capskeys:
            res[k] = mapping[k]
    return res

def printMapping(mapping, associations, context = None):
    for k in mapping:
        if k in associations:
            if context is None:
                print("  {:-<15}-> {}".format(ecodesNames[k], associations[k]))
            else:
                if associations[k] in context["keys"]:
                    if type(context["keys"][associations[k]]) is list:
                        str = ""
                        for x in context["keys"][associations[k]]:
                            if str != "":
                                str = str + ", "
                            str = str + ecodesNames[x]
                        print("  {:-<15}-> {:-<15}-> {}".format(ecodesNames[k], associations[k], str))
                    else:
                        print("  {:-<15}-> {:-<15}-> {}".format(ecodesNames[k], associations[k], ecodesNames[context["keys"][associations[k]]]))
                else:
                    print("  {:-<15}-> {:15}".format(ecodesNames[k], associations[k]))

def handle_actions(devices, nodes_by_fd, mappings, poll, action, device):
    if device.device_node is not None and device.device_node[:16] == "/dev/input/event":
        if action == "add":
            dev = { "node": device.device_node, "dev": evdev.InputDevice(device.device_node) }
            if dev["dev"].name != DEVICE_NAME:
                caps = dev["dev"].capabilities()
                if ecodes.EV_KEY in caps:
                    mapping = getMapping(dev["dev"])
                    associations = getMappingAssociations(mapping, caps)
                    if len(associations) > 0:
                        if gdebug:
                            print("Adding device {}: {}".format(device.device_node, dev["dev"].name))
                            printMapping(mapping, associations)
                        devices[device.device_node] = dev
                        nodes_by_fd[dev["dev"].fileno()] = device.device_node
                        mappings[dev["dev"].fileno()] = mapping
                        poll.register(dev["dev"].fileno(), select.POLLIN)
        elif action == "remove":
            if device.device_node in devices:
                if gdebug:
                    print("Removing device {}: {}".format(device.device_node, devices[device.device_node]["dev"].name))
                poll.unregister(devices[device.device_node]["dev"].fileno())
                del nodes_by_fd[devices[device.device_node]["dev"].fileno()]
                del mappings[devices[device.device_node]["dev"].fileno()]
                del devices[device.device_node]

def handle_event(target, event, action, context):
    if action in context["keys"]:
        if gdebug:
            print("code:{}, value:{}, action:{}".format(event.code, event.value, action))
        sendKeys(target, context["keys"][action])

def sendKeys(target, keys):
    if type(keys) is list:
        for x in keys:
            target.write(ecodes.EV_KEY, x, 1)
            target.syn()
        time.sleep(0.1) # time required for emulators (like mame) based on states and not on events (if you go too fast, the event is not seen)
        for x in keys:
            target.write(ecodes.EV_KEY, x, 0)
            target.syn()
    else:
        target.write(ecodes.EV_KEY, keys, 1)
        target.syn()
        time.sleep(0.1) # time required for emulators (like mame) based on states and not on events (if you go too fast, the event is not seen)
        target.write(ecodes.EV_KEY, keys, 0)
        target.syn()


def do_send(key):
    if key not in knownActions:
        print("unknown action {}".format(knownActions))
        exit(1)

    context = getContext()
    sender_keys = []
    if key in context["keys"]:
        if type(context["keys"][key]) is list:
            for x in context["keys"][key]:
                sender_keys.append(x)
        else:
            sender_keys.append(context["keys"][key])
    sender = evdev.UInput(name="virtual keyboard", events={ ecodes.EV_KEY: sender_keys })
    sendKeys(sender, sender_keys)

def readPid():
    with open(gpid_file, 'r') as fd:
        return fd.read().replace('\n', '')

def writePid():
    with open(gpid_file, "w") as fd:
        fd.write(str(os.getpid()))
    
def do_new_context(context_name = None, context_json = None):
    if context_name is not None and context_json is not None:
        data = {}
        data["name"] = context_name
        data["keys"] = json.loads(context_json)
        context = loadContext(data)
        # update the config file
        saveContext(context, gcontext_file)
    else:
        if os.path.exists(gcontext_file):
            os.remove(gcontext_file)

    # inform the process
    pid = int(readPid())
    os.kill(pid, signal.SIGHUP)

def signal_sigup(signum, frame):
    gcontext = getContext()

def do_list():
    gcontext = getContext()

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')

    printContext(gcontext)

    for device in context.list_devices(subsystem='input'):
        if device.device_node is not None and device.device_node[:16] == "/dev/input/event":
            dev = { "node": device.device_node, "dev": evdev.InputDevice(device.device_node) }
            if dev["dev"].name != DEVICE_NAME:
                caps = dev["dev"].capabilities()
                if ecodes.EV_KEY in caps:
                    mapping = getMapping(dev["dev"])
                    associations = getMappingAssociations(mapping, caps)
                    if len(associations) > 0:
                        fullpath = getMappingFullPath(dev["dev"])
                        fname = getDeviceConfigFilename(dev["dev"])
                        if fullpath:
                            print("# device {} [{}] ({})".format(device.device_node, dev["dev"].name, fullpath))
                        else:
                            print("# device {} [{}] (no {} file found)".format(device.device_node, dev["dev"].name, fname))
                        printMapping(mapping, associations, gcontext)

def run(args):
    devices = {}
    nodes_by_fd = {}
    mappings = {}

    gcontext = getContext()

    # permanent : write a pid so that new configuration can apply
    if args.permanent:
        writePid()

    # monitor all udev devices
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')
    monitor.start()

    poll = select.poll()
    poll.register(monitor.fileno(), select.POLLIN)

    # adding existing devices in the poll
    for device in context.list_devices(subsystem='input'):
        handle_actions(devices, nodes_by_fd, mappings, poll, "add", device)

    # target virtual keyboard
    target_keys = []
    for x in range(ecodes.KEY_MAX):
        if x in ecodesNames:
            target_keys.append(x)
    target = evdev.UInput(name=DEVICE_NAME, events={ ecodes.EV_KEY: target_keys })

    # to read new contexts
    signal.signal(signal.SIGHUP, signal_sigup)

    # read all devices
    while True:
        for fd, _ in poll.poll():
            try:
                if fd == monitor.fileno():
                    (action, device) = monitor.receive_device()
                    handle_actions(devices, nodes_by_fd, mappings, poll, action, device)
                else:
                    event = devices[nodes_by_fd[fd]]["dev"].read_one()
                    if event.type == ecodes.EV_KEY and event.value == 0 and event.code in mappings[fd]: # limit to key down
                        handle_event(target, event, mappings[fd][event.code], gcontext)
            except (OSError, KeyError):
                pass # ok, error on the device
            except:
                target.close()
                raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="hotkeygen")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--send")
    parser.add_argument("--default-context", action="store_true")
    parser.add_argument("--new-context", nargs=2, metavar=("new-context-name", "new-context-json"))
    parser.add_argument("--permanent", action="store_true")
    args = parser.parse_args()
    if args.debug:
        gdebug = True

    if args.list:
        do_list()
    elif args.send is not None:
        do_send(args.send)
    elif args.new_context is not None:
        new_context_name, new_context_json = args.new_context
        do_new_context(new_context_name, new_context_json)
    elif args.default_context:
        do_new_context()
    else:
        run(args)
#####
