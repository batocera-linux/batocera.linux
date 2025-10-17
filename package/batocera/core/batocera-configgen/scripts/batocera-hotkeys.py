#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

SYSTEM_HOTKEYS_FILE = Path("/usr/share/evmapy/hotkeys.keys")
USER_HOTKEYS_FILE = Path("/userdata/system/configs/hotkeys.keys")
HOTKEYGEN_MAPPING = Path("/etc/hotkeygen/default_mapping.conf")

def read_config(system_config_file: Path, user_config_file: Path, systemOnly: bool = False):
    if user_config_file.exists() and systemOnly == False:
        try:
            config = json.loads(user_config_file.read_text())
            return config
        except:
            print("Unable to read user file {}".format(user_config_file), file=sys.stderr)

    config = json.loads(system_config_file.read_text())
    return config

def read_hotkey_mapping(hotkey_mapping_file: Path):
    mapping = json.loads(hotkey_mapping_file.read_text())
    by_keys = mapping

    non_game_hotkeys = ["KEY_FILE"]

    # remove hotkeys not for games
    for k in non_game_hotkeys:
        if k in by_keys:
            del by_keys["KEY_FILE"]
    
    by_names = {}
    for m in by_keys:
        by_names[by_keys[m]] = m
    return { "by_keys": by_keys, "by_names": by_names}

def list_hotkeys(config: dict, default_config: dict, hotkeys_mapping: dict):
    if sys.stdout.isatty():
        list_hotkeys_text(config, default_config, hotkeys_mapping)
    else:
        list_hotkeys_xml(config, default_config, hotkeys_mapping)

def isSimpleKey(key):
    return isinstance(key["trigger"], list) and len(key["trigger"]) == 2 and key["trigger"][0] == "hotkey" and key["type"] == "key" and isinstance(key["target"], list) and len(key["target"]) == 1

def getKeysFromConfig(config):
    keys = {}
    for key in config["actions_player1"]:
        if isSimpleKey(key):
            btn = key["trigger"][1]
            action = key["target"][0]
            keys[btn] = {"action": action}
    return keys

def list_hotkeys_xml(config: dict, default_config: dict, hotkeys_mapping: dict):
    keys = getKeysFromConfig(config)
    default_keys = getKeysFromConfig(default_config)
    order = ["start", "select", "up", "down", "left", "right", "a", "b", "x", "y", "pageup", "pagedown", "l2", "r2", "l3", "r3"]

    sorted_keys = {}
    for k in order:
        if k in keys:
            sorted_keys[k] = keys[k]
        else:
            sorted_keys[k] = None
    for k in keys:
        if k not in sorted_keys:
            sorted_keys[k] = keys[k]

    print("<hotkeys>")
    for btn in sorted_keys:
        action_name = ""
        default_action_name = ""

        if btn in keys:
            action_name = "unknown ({})".format(keys[btn]["action"])
            if keys[btn]["action"] in hotkeys_mapping["by_keys"]:
                action_name = hotkeys_mapping["by_keys"][keys[btn]["action"]]

        if btn in default_keys:
            default_action_name = "unknown ({})".format(default_keys[btn]["action"])
            if default_keys[btn]["action"] in hotkeys_mapping["by_keys"]:
                default_action_name = hotkeys_mapping["by_keys"][default_keys[btn]["action"]]

        print("  <hotkey button=\"{}\" action=\"{}\" default=\"{}\" />".format(btn, action_name, default_action_name))
        
    print("</hotkeys>")

def list_hotkeys_text(config: dict, default_config: dict, hotkeys_mapping: dict):
    keys = getKeysFromConfig(config)
    default_keys = getKeysFromConfig(default_config)
    order = ["start", "select", "up", "down", "left", "right", "a", "b", "x", "y", "pageup", "pagedown", "l2", "r2", "l3", "r3"]

    sorted_keys = {}
    for k in order:
        if k in keys:
            sorted_keys[k] = keys[k]
        else:
            sorted_keys[k] = None
    for k in keys:
        if k not in sorted_keys:
            sorted_keys[k] = keys[k]

    for btn in sorted_keys:
        action_name = None
        default_action_name = None

        if btn in keys:
            action_name = "unknown ({})".format(keys[btn]["action"])
            if keys[btn]["action"] in hotkeys_mapping["by_keys"]:
                action_name = hotkeys_mapping["by_keys"][keys[btn]["action"]]

        if btn in default_keys:
            default_action_name = "unknown ({})".format(default_keys[btn]["action"])
            if default_keys[btn]["action"] in hotkeys_mapping["by_keys"]:
                default_action_name = hotkeys_mapping["by_keys"][default_keys[btn]["action"]]

        if btn == "pageup":
            btn = "l"
        if btn == "pagedown":
            btn = "r"

        help = ""
        if action_name != default_action_name:
            help = " (default: {})".format(default_action_name)
        print("hotkey + {:6} : {}{}".format(btn, action_name, help))

def update_hotkeys(config: dict, new_keys: dict, user_config_file: Path, default_config: dict):
    # update keys
    for new_key in new_keys:
        found = False
        for index, key in enumerate(config["actions_player1"]):
            if isSimpleKey(key):
                if key["trigger"][1] == new_key:
                    found = True
                    if new_keys[new_key] == "none":
                        del config["actions_player1"][index]
                    else:
                        if new_keys[new_key] == "default":
                            # get default
                            for default_key in default_config["actions_player1"]:
                                if isSimpleKey(default_key):
                                    if default_key["trigger"][1] == new_key:
                                        config["actions_player1"][index]["target"] = default_key["target"]
                        else:
                            config["actions_player1"][index]["target"] = [ new_keys[new_key] ]
        # the key was removed, add it back from default config
        if not found:
            if new_keys[new_key] != "none":
                for key in default_config["actions_player1"]:
                    if isSimpleKey(key):
                        if key["trigger"][1] == new_key:
                            # find the default key and append it
                            if new_keys[new_key] != "default":
                                key["target"] = [ new_keys[new_key] ]
                            config["actions_player1"].append(key)

    # save
    with open(user_config_file, "w") as fd:
        json.dump(config, fd, indent=4)

def list_values(hotkeys_mapping):
    for key in sorted(hotkeys_mapping["by_names"]):
        print(key)
        
parser = argparse.ArgumentParser(prog="batocera-hotkeys")
parser.add_argument("--values", action="store_true", help="list possible values. none and default can be used too.")
parser.add_argument("--start", type=str, help="key for hotkey+start")
parser.add_argument("--select", type=str, help="key for hotkey+select")
parser.add_argument("--up", type=str, help="key for hotkey+up")
parser.add_argument("--down", type=str, help="key for hotkey+down")
parser.add_argument("--left", type=str, help="key for hotkey+left")
parser.add_argument("--right", type=str, help="key for hotkey+right")
parser.add_argument("--a", type=str, help="key for hotkey+a")
parser.add_argument("--b", type=str, help="key for hotkey+b")
parser.add_argument("--x", type=str, help="key for hotkey+x")
parser.add_argument("--y", type=str, help="key for hotkey+y")
parser.add_argument("--l", type=str, help="key for hotkey+l")
parser.add_argument("--r", type=str, help="key for hotkey+r")
parser.add_argument("--pageup", type=str, help="key for hotkey+l")
parser.add_argument("--pagedown", type=str, help="key for hotkey+r")
parser.add_argument("--l2", type=str, help="key for hotkey+l2")
parser.add_argument("--r2", type=str, help="key for hotkey+r2")
parser.add_argument("--l3", type=str, help="key for hotkey+l3")
parser.add_argument("--r3", type=str, help="key for hotkey+r3")

args = parser.parse_args()
new_keys = {}

if args.start:
    new_keys["start"] = args.start
if args.select:
    new_keys["select"] = args.select
if args.up:
    new_keys["up"] = args.up
if args.down:
    new_keys["down"] = args.down
if args.left:
    new_keys["left"] = args.left
if args.right:
    new_keys["right"] = args.right
if args.a:
    new_keys["a"] = args.a
if args.b:
    new_keys["b"] = args.b
if args.x:
    new_keys["x"] = args.x
if args.y:
    new_keys["y"] = args.y
if args.l:
    new_keys["pageup"] = args.l
if args.r:
    new_keys["pagedown"] = args.r
if args.pageup:
    new_keys["pageup"] = args.pageup
if args.pagedown:
    new_keys["pagedown"] = args.pagedown
if args.l2:
    new_keys["l2"] = args.l2
if args.r2:
    new_keys["r2"] = args.r2
if args.l3:
    new_keys["l3"] = args.l3
if args.r3:
    new_keys["r3"] = args.r3

hotkeys_mapping = read_hotkey_mapping(HOTKEYGEN_MAPPING)

if args.values:
    list_values(hotkeys_mapping)
    exit(0)

default_config  = read_config(SYSTEM_HOTKEYS_FILE, USER_HOTKEYS_FILE, True)
config          = read_config(SYSTEM_HOTKEYS_FILE, USER_HOTKEYS_FILE)

# convert new keys
for k in new_keys:
    if new_keys[k] in hotkeys_mapping["by_names"]:
        new_keys[k] = hotkeys_mapping["by_names"][new_keys[k]]

if len(new_keys) == 0:
    list_hotkeys(config, default_config, hotkeys_mapping)
else:
    update_hotkeys(config, new_keys, USER_HOTKEYS_FILE, default_config)
