# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, cast
from dataclasses import dataclass

_logger = logging.getLogger(__name__)
_input_re: Final = re.compile(r'^/dev/input/event([0-9]*)$')

db_system = Path("/usr/share/batocera/launch/data/trackballspinners.yaml")

@dataclass(slots=True, kw_only=True)
class TrackballSpinner:
    name: str
    path: str
    type: str
    rels: [int]
    device_path: str
    mouseid: int

    @staticmethod
    def get_all() -> (TrackballSpinnerList, TrackballSpinnerList):
        eligible_events = TrackballSpinner.getEligibleEvents()
        db = TrackballSpinner.getDb()
        events = TrackballSpinner.filterEventsByDB(eligible_events, db)
        trackballspinners: TrackballSpinnerList = []

        for event in events:
            trackballspinner = TrackballSpinner(
                name = event["name"],
                path = event["event"]["path"],
                type = event["type"],
                rels = event["axis"],
                device_path = event["event"]["device_path"],
                mouseid = event["event"]["mouseid"]
            )
            trackballspinners.append(trackballspinner)
            _logger.info(
                'found %s at %s with mouseid=%i and name=%s', event["type"], event["event"]["path"], event["event"]["mouseid"], event["name"]
            )

        # sort by path (usb position), then axis to get always the same order after reboots (axis is needed cause you can have several spinners on the same input
        trackballspinners = sorted(trackballspinners, key=TrackballSpinner.sort_events)

        if not trackballspinners:
            _logger.info('no trackball nor spinner found')

        # split trackballs and spinners
        trackballs = [item for item in trackballspinners if item.type == 'trackball']
        spinners   = [item for item in trackballspinners if item.type == 'spinner']

        return (trackballs, spinners)

    @staticmethod
    def sort_events(item):
        rels = item.rels
        if isinstance(rels, str):
            rels_key = [rels]
        else:
            rels_key = rels

        # sort by path, then axis
        return (item.device_path, rels_key)

    @staticmethod
    def getDb():
        import yaml
        with open(db_system, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def filterEventsByDB(eligible_events, db):
        values = []
        for event in eligible_events:
            for ke in db:
                if ke["device_name"] == event["name"] and ke["vendor"] == event["vendor"] and ke["product"] == event["product"]:
                    if not ("version" in ke and ke["version"] != event["version"]):
                        if not ("interface" in ke and ke["interface"] != event["interface"]):
                            values.append({"name": ke["name"], "type": ke["type"], "axis": ke["axis"], "event": {"id": event["id"], "path": event["path"], "mouseid": event["mouseid"], "device_path": event["device_path"]}})
        return values

    @staticmethod
    def getEligibleEvents():
        import evdev
        import pyudev

        context = pyudev.Context()

        ev_rel_valid = {
            evdev.ecodes.REL_X:  "REL_X",
            evdev.ecodes.REL_Y:  "REL_Y",
            # i suggest to enable only if we discover a hardware using them
            #    evdev.ecodes.REL_Z:  "REL_Z",
            #    evdev.ecodes.REL_RX: "REL_RX",
            #    evdev.ecodes.REL_RY: "REL_RY",
            #    evdev.ecodes.REL_RZ: "REL_RZ",
        }

        # get mice to get mice indexes
        mouses = {
            int(match.group(1)): mouse
            for mouse in context.list_devices(subsystem='input')
            if mouse.device_node is not None
            and (match := _input_re.match(mouse.device_node)) is not None
            and mouse.properties.get('ID_INPUT_MOUSE') == '1'
        }
        mouses_ids = {}
        for mouseid, (_, mouse) in enumerate(sorted(mouses.items(), key=lambda item: item[0])):
            mouses_ids[mouse.device_node] = mouseid

        eligible_events = []
        for event in context.list_devices(subsystem='input'):
            if event.device_node is not None:
                match = _input_re.match(event.device_node)
                if match is not None:
                    id = int(match.group(1))
                    device = evdev.InputDevice(cast('str', event.device_node))
                    caps = device.capabilities()
                    if evdev.ecodes.EV_REL in caps:
                        ev_rel = caps[evdev.ecodes.EV_REL]
                        if any(axis in ev_rel for axis in ev_rel_valid):
                            raw_interface = event.get("ID_USB_INTERFACE_NUM")
                            interface_num = int(raw_interface) if raw_interface is not None else 0
                            eligible_events.append({
                                "id": id,
                                "ev_rel": [ev_rel_valid[code] for code in ev_rel if code in ev_rel_valid],
                                "vendor": device.info.vendor,
                                "product": device.info.product,
                                "version": device.info.version,
                                "name": device.name,
                                "interface": interface_num,
                                "path": device.path,
                                "device_path": event.device_path,
                                "mouseid": mouses_ids[event.device_node] if event.device_node in mouses_ids else None
                            })
        return eligible_events


type TrackballSpinnerList = list[TrackballSpinner]


def main() -> None:
    trackballs, spinners = TrackballSpinner.get_all()
    if len(trackballs) > 0:
        print("Trackballs :")
        print("=" * 50)
        for n, trackball in enumerate(trackballs, 1):
            print(f"  • {trackball.name:<37} Player {n}")
            print(f"    ├─ event:   {trackball.path}")
            print(f"    ├─ axis:    {trackball.rels}")
            print(f"    └─ mouseid: {trackball.mouseid}")
            print("")
    if len(spinners) > 0:
        print("Spinners:")
        print("=" * 50)
        for n, spinner in enumerate(spinners, 1):
            print(f"  • {spinner.name:<37} Player {n}")
            print(f"    ├─ event:   {spinner.path}")
            print(f"    ├─ axis:    {spinner.rels}")
            print(f"    └─ mouseid: {spinner.mouseid}")
            print("")

if __name__ == '__main__':
    main()
