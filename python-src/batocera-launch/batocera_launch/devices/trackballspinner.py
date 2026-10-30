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

import argparse
import hashlib
import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, cast

_logger = logging.getLogger(__name__)
_input_re: Final = re.compile(r'^/dev/input/event([0-9]*)$')

db_system = Path('/usr/share/batocera/launch/data/trackballspinners.yaml')
db_user = Path('/userdata/system/configs/trackballspinners.yaml')


# representation of an udev event (with extra information like mouseid)
@dataclass(slots=True, kw_only=True)
class TrackballSpinnerEvent:
    axis: list[str]
    vendor: int
    product: int
    version: int
    name: str
    interface: int
    path: str
    device_path: str
    mouseid: int | None  # None should not happen ; in case ID_INPUT_MOUSE is not set

    # an event identifier for a trackball or spinner event is composed of different element identified here
    # version can be unused to match several devices
    # interface can be used cause some devices creates several similar events, but with different interfaces
    def get_identifier(
        self, type: str, use_version: bool, use_interface: bool, axis: str | list[str]
    ) -> tuple[Any, ...]:
        # key to remove duplicates, name can differ
        keys_to_match = ('name', 'vendor', 'product', 'version', 'interface')

        identifier: list[Any] = [type]
        for k in keys_to_match:
            val: Any
            if (k == 'version' and not use_version) or (k == 'interface' and not use_interface):
                val = None
            else:
                val = getattr(self, k)
            if isinstance(val, list):
                val = tuple(cast('list[Any]', val))
            identifier.append(val)
        identifier.append(axis)

        return tuple(identifier)

    # key to share out of the program to then register or remove from database
    def get_identifier_key(self, type: str, use_version: bool, use_interface: bool, axis: str | list[str]) -> str:
        return hashlib.md5(
            str(self.get_identifier(type, use_version, use_interface, axis)).encode('utf-8')
        ).hexdigest()[:8]

    @staticmethod
    def getEligibleEvents() -> list[TrackballSpinnerEvent]:
        import evdev
        import pyudev

        context = pyudev.Context()

        ev_rel_valid = {
            evdev.ecodes.REL_X: 'REL_X',
            evdev.ecodes.REL_Y: 'REL_Y',
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
        mouses_ids: dict[str, int] = {}
        for mouseid, (_, mouse) in enumerate(sorted(mouses.items(), key=lambda item: item[0])):
            mouses_ids[cast('str', mouse.device_node)] = mouseid

        eligible_events: list[TrackballSpinnerEvent] = []
        for event in context.list_devices(subsystem='input'):
            if event.device_node is not None:
                match = _input_re.match(event.device_node)
                if match is not None:
                    device = evdev.InputDevice(event.device_node)
                    caps = device.capabilities()
                    if evdev.ecodes.EV_REL in caps:
                        ev_rel = caps[evdev.ecodes.EV_REL]
                        if any(axis in ev_rel for axis in ev_rel_valid):
                            raw_interface: str | None = event.properties.get('ID_USB_INTERFACE_NUM')
                            interface_num: int = int(raw_interface) if raw_interface is not None else 0
                            eligible_event = TrackballSpinnerEvent(
                                axis=[ev_rel_valid[code] for code in ev_rel if code in ev_rel_valid],
                                vendor=device.info.vendor,
                                product=device.info.product,
                                version=device.info.version,
                                name=device.name,
                                interface=interface_num,
                                path=device.path,
                                device_path=event.device_path,
                                mouseid=mouses_ids.get(event.device_node),
                            )
                            eligible_events.append(eligible_event)
        return eligible_events


# representation of a trackball or spinner in the database
@dataclass(slots=True, kw_only=True)
class TrackballSpinnerDB:
    name: str
    type: str
    device_name: str
    vendor: int
    product: int
    version: int | None
    interface: int | None
    axis: str | list[str]

    def get_identifier(self) -> tuple[Any, ...]:
        # key to remove duplicates, name can differ
        keys_to_match = ('type', 'device_name', 'vendor', 'product', 'version', 'interface', 'axis')

        identifier: list[Any] = [type]
        for k in keys_to_match:
            val: Any
            val = getattr(self, k)
            if isinstance(val, list):
                val = tuple(cast('list[Any]', val))
            identifier.append(val)
        return tuple(identifier)

    # key to share out of the program to then register or remove from database
    def get_identifier_key(self) -> str:
        return hashlib.md5(str(self.get_identifier()).encode('utf-8')).hexdigest()[:8]

    def toDbElement(self) -> dict[str, Any]:
        val: dict[str, Any] = {
            'name': self.name,
            'type': self.type,
            'axis': self.axis,
            'device_name': self.name,
            'vendor': self.vendor,
            'product': self.product,
            'version': self.version,
        }
        if self.interface is not None:
            val['interface'] = self.interface
        return val

    @staticmethod
    def getDb(userOnly: bool = False) -> dict[tuple[Any, ...], TrackballSpinnerDB]:
        import yaml

        db_system_data: list[dict[str, Any]]
        db_user_data: list[dict[str, Any]]

        # system db
        if userOnly:
            db_system_data = []
        else:
            with Path(db_system).open(encoding='utf-8') as f:
                db_system_data = yaml.safe_load(f) or []

        # user db
        try:
            with Path(db_user).open(encoding='utf-8') as f:
                db_user_data = yaml.safe_load(f) or []
        except (FileNotFoundError, PermissionError, yaml.YAMLError) as e:  # any error on the user file, we ignore
            _logger.info('unable to read user file: %s: %s', db_user, e)
            db_user_data = []

        # index systems keys
        merged_dict: dict[tuple[Any], TrackballSpinnerDB] = {}

        for item in db_system_data:
            db_elt = TrackballSpinnerDB(
                name=item['name'],
                type=item['type'],
                device_name=item['device_name'],
                vendor=item['vendor'],
                product=item['product'],
                version=item.get('version'),
                interface=item.get('interface'),
                axis=item['axis'],
            )
            merged_dict[db_elt.get_identifier()] = db_elt

        # adding user db
        for item in db_user_data:
            # prefer the user key than the db key
            db_elt = TrackballSpinnerDB(
                name=item['name'],
                type=item['type'],
                device_name=item['device_name'],
                vendor=item['vendor'],
                product=item['product'],
                version=item['version'],
                interface=item.get('interface'),
                axis=item['axis'],
            )
            merged_dict[db_elt.get_identifier()] = db_elt

        return merged_dict

    @staticmethod
    def saveUserDb(db_user_data: list[dict[str, Any]]) -> None:
        import yaml

        with Path(db_user).open('w', encoding='utf-8') as f:
            yaml.safe_dump(db_user_data, f, allow_unicode=True, sort_keys=False)

    @staticmethod
    def eventMatchesDB(
        event: TrackballSpinnerEvent, db: TrackballSpinnerDB, type: str | None = None, axis: str | None = None
    ) -> bool:
        return (
            (type is None or db.type == type)
            and (axis is None or db.axis == axis)
            and db.device_name == event.name
            and db.vendor == event.vendor
            and db.product == event.product
            and
            # not mandatory fields
            (db.version is None or db.version == event.version)
            and (db.interface is None or db.interface == event.interface)
        )

    @staticmethod
    def eventMatchesDBAny(
        event: TrackballSpinnerEvent,
        db: dict[tuple[Any, ...], TrackballSpinnerDB],
        type: str | None = None,
        axis: str | None = None,
    ) -> bool:
        return any(TrackballSpinnerDB.eventMatchesDB(event, db[ke], type, axis) for ke in db)


# representation of a trackball or spinner physical instance to present to emulators configs (a mix of db information + udev informations)
@dataclass(slots=True, kw_only=True)
class TrackballSpinner:
    name: str
    path: str
    type: str
    axis: str | list[str]
    device_path: str
    mouseid: int | None  # None should not happen ; in case ID_INPUT_MOUSE is not set
    use_interface: bool  # if True, record the interface when registering
    key: str
    event: TrackballSpinnerEvent  # trace of the event to register it

    @staticmethod
    def get_all(suggest: bool = False) -> tuple[TrackballSpinnerList, TrackballSpinnerList]:
        eligible_events: list[TrackballSpinnerEvent] = TrackballSpinnerEvent.getEligibleEvents()
        db: dict[tuple[Any, ...], TrackballSpinnerDB] = TrackballSpinnerDB.getDb()
        trackballspinners: list[TrackballSpinner] = []

        if suggest:
            trackballspinners = TrackballSpinner.filterSuggestedEventsByDB(eligible_events, db)
        else:
            trackballspinners = TrackballSpinner.filterEventsByDB(eligible_events, db)

        # sort by path (usb position), then axis to get always the same order after reboots (axis is needed cause you can have several spinners on the same input
        trackballspinners = sorted(trackballspinners, key=TrackballSpinner.sort_events)

        if not trackballspinners:
            _logger.info('no trackball nor spinner found')

        # split trackballs and spinners
        trackballs = [item for item in trackballspinners if item.type == 'trackball']
        spinners = [item for item in trackballspinners if item.type == 'spinner']

        return (trackballs, spinners)

    @staticmethod
    def sort_events(item: TrackballSpinner) -> tuple[str, str | list[str]]:
        axis = item.axis
        if isinstance(axis, str):
            axis_key = [axis]
        else:
            axis_key = axis

        # sort by path, then axis
        return (item.device_path, axis_key)

    @staticmethod
    def filterEventsByDB(
        eligible_events: list[TrackballSpinnerEvent], db: dict[tuple[Any, ...], TrackballSpinnerDB]
    ) -> list[TrackballSpinner]:
        return [
            TrackballSpinner(
                name=db[ke].name,
                path=event.path,
                type=db[ke].type,
                axis=db[ke].axis,
                device_path=event.device_path,
                mouseid=event.mouseid,
                key=db[ke].get_identifier_key(),
                use_interface=db[ke].interface is not None,
                event=event,
            )
            for event in eligible_events
            for ke in db
            if TrackballSpinnerDB.eventMatchesDB(event, db[ke])
        ]

    @staticmethod
    def filterSuggestedEventsByDB(
        eligible_events: list[TrackballSpinnerEvent], db: dict[tuple[Any, ...], TrackballSpinnerDB]
    ) -> list[TrackballSpinner]:
        values: list[TrackballSpinner] = []

        # search if version and interface are important or not (some devices, when plugged, present 2 times the same hardware, but on 2 different interfaces (like xarcade))
        events_with_duplicate_product_vendor_version_but_different_interface = {}
        for event1 in eligible_events:
            for event2 in eligible_events:
                if event1.path != event2.path and (
                    event1.vendor == event2.vendor
                    and event1.product == event2.product
                    and event1.version == event2.version
                    and event1.interface != event2.interface
                ):
                    # while it is a double loop, event2 will be added too
                    key = str(event1.vendor) + '_' + str(event1.product)
                    if key not in events_with_duplicate_product_vendor_version_but_different_interface:
                        events_with_duplicate_product_vendor_version_but_different_interface[key] = 0
                    events_with_duplicate_product_vendor_version_but_different_interface[key] += 1

        for event in eligible_events:
            # set to True only if there are many devices matching in eligible_events
            key = str(event.vendor) + '_' + str(event.product)
            use_version = (
                True  # ok, use always cause some devices where product/vendor but not the same version (xarcade)
            )
            use_interface = key in events_with_duplicate_product_vendor_version_but_different_interface

            # trackball
            if (
                not TrackballSpinnerDB.eventMatchesDBAny(event, db, 'trackball')
                and 'REL_X' in event.axis
                and 'REL_Y' in event.axis
            ):
                values.append(
                    TrackballSpinner(
                        name=event.name,
                        path=event.path,
                        type='trackball',
                        axis=['REL_X', 'REL_Y'],  # suggest only with rel_x and rel_y
                        device_path=event.device_path,
                        mouseid=event.mouseid,
                        key=event.get_identifier_key('trackball', use_version, use_interface, ['REL_X', 'REL_Y']),
                        use_interface=use_interface,
                        event=event,
                    )
                )

            # spinner
            values.extend(
                TrackballSpinner(
                    name=event.name,
                    path=event.path,
                    type='spinner',
                    axis=axis,
                    device_path=event.device_path,
                    mouseid=event.mouseid,
                    key=event.get_identifier_key('spinner', use_version, use_interface, axis),
                    use_interface=use_interface,
                    event=event,
                )
                for axis in ['REL_X', 'REL_Y']
                if not TrackballSpinnerDB.eventMatchesDBAny(event, db, 'spinner', axis) and axis in event.axis
            )

        return values

    def toDbElement(self) -> dict[str, Any]:
        val: dict[str, Any] = {
            'name': self.name,
            'type': self.type,
            'axis': self.axis,
            'device_name': self.event.name,
            'vendor': self.event.vendor,
            'product': self.event.product,
            'version': self.event.version,
        }
        if self.use_interface:
            val['interface'] = self.event.interface
        return val

    def register(self):
        import yaml

        db_user_data: list[dict[str, Any]]
        db_element: dict[str, Any] = self.toDbElement()

        # read, add, write, user db
        path = Path(db_user)
        if path.exists():
            with path.open(encoding='utf-8') as f:
                db_user_data = yaml.safe_load(f) or []
        else:
            db_user_data = []

        db_user_data.append(db_element)

        with Path(db_user).open('w', encoding='utf-8') as f:
            yaml.safe_dump(db_user_data, f, allow_unicode=True, sort_keys=False)


type TrackballSpinners = Sequence[TrackballSpinner]
type TrackballSpinnerList = list[TrackballSpinner]


def main_display_xml(trackballs: list[TrackballSpinner], spinners: list[TrackballSpinner]) -> None:
    from xml.dom.minidom import Document, parseString

    from dicttoxml2 import dicttoxml

    vals = [{'name': x.name, 'type': x.type, 'axis': x.axis, 'key': x.key} for x in trackballs]
    vals.extend({'name': x.name, 'type': x.type, 'axis': x.axis, 'key': x.key} for x in spinners)

    xml_bytes: bytes = dicttoxml(
        vals,
        custom_root='trackballspinners',
        item_func=lambda x: 'trackballspinner',
        attr_type=False,
    )
    dom: Document = parseString(xml_bytes)
    print(dom.toprettyxml())


def main_list(as_xml: bool) -> None:
    # just list devices
    trackballs, spinners = TrackballSpinner.get_all()

    if as_xml:
        main_display_xml(trackballs, spinners)
    else:
        if len(trackballs) > 0:
            print('Trackballs :')
            print('=' * 50)
            for n, trackball in enumerate(trackballs, 1):
                print(f'  • {trackball.name:<37} Player {n}')
                print(f'    ├─ event:   {trackball.path}')
                print(f'    ├─ axis:    {trackball.axis}')
                print(f'    ├─ mouseid: {trackball.mouseid}')
                print(f'    └─ key:     {trackball.key}')
                print('')
        if len(spinners) > 0:
            print('Spinners:')
            print('=' * 50)
            for n, spinner in enumerate(spinners, 1):
                print(f'  • {spinner.name:<37} Player {n}')
                print(f'    ├─ event:   {spinner.path}')
                print(f'    ├─ axis:    {spinner.axis}')
                print(f'    ├─ mouseid: {spinner.mouseid}')
                print(f'    └─ key:     {spinner.key}')
                print('')


def main_suggest(as_xml: bool) -> None:
    trackballs, spinners = TrackballSpinner.get_all(suggest=True)
    if as_xml:
        main_display_xml(trackballs, spinners)
    else:
        if len(trackballs) > 0:
            print('Trackballs :')
            print('=' * 50)
            for _n, trackball in enumerate(trackballs, 1):
                print(f'  • {trackball.name}')
                print(f'    ├─ event:   {trackball.path}')
                print(f'    ├─ axis:    {trackball.axis}')
                print(f'    ├─ mouseid: {trackball.mouseid}')
                print(f'    └─ key:     {trackball.key}')
                print('')
        if len(spinners) > 0:
            print('Spinners:')
            print('=' * 50)
            for _n, spinner in enumerate(spinners, 1):
                print(f'  • {spinner.name}')
                print(f'    ├─ event:   {spinner.path}')
                print(f'    ├─ axis:    {spinner.axis}')
                print(f'    ├─ mouseid: {spinner.mouseid}')
                print(f'    └─ key:     {spinner.key}')
                print('')


def main_register_device(device_key: str) -> None:
    eligible_events: list[TrackballSpinnerEvent] = TrackballSpinnerEvent.getEligibleEvents()
    db: dict[tuple[Any, ...], TrackballSpinnerDB] = TrackballSpinnerDB.getDb()
    trackballspinners: list[TrackballSpinner] = TrackballSpinner.filterSuggestedEventsByDB(eligible_events, db)

    for trackballspinner in trackballspinners:
        if trackballspinner.key == device_key:
            print(f'Registering device {trackballspinner.name}')
            trackballspinner.register()
            return


def main_unregister_device(device_key: str) -> None:
    # find the device to remove
    element_to_remove = None
    trackballs, spinners = TrackballSpinner.get_all()
    for element in trackballs:
        if element.key == device_key:
            element_to_remove = element
    for element in spinners:
        if element.key == device_key:
            element_to_remove = element

    # remove the element among the user database
    if element_to_remove is not None:
        userdb: dict[tuple[Any, ...], TrackballSpinnerDB] = TrackballSpinnerDB.getDb(True)
        userdb_new: list[dict[str, Any]] = []
        for ke in userdb:
            if TrackballSpinnerDB.eventMatchesDB(
                element_to_remove.event,
                userdb[ke],
                element_to_remove.type,
                cast('str', element_to_remove.axis) if element_to_remove.type == 'spinner' else None,
            ):
                print(f'Unregistering device {element_to_remove.name}')
            else:
                userdb_new.append(userdb[ke].toDbElement())
        TrackballSpinnerDB.saveUserDb(userdb_new)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--list', action='store_true', help='List identified trackballs and spinners')
    parser.add_argument(
        '--suggest-new-devices', action='store_true', help='List devices that may be trackball or spinner'
    )
    parser.add_argument('--register-device', type=str, help='Mark a device as real')
    parser.add_argument('--unregister-device', type=str, help='Unmark a device as real')
    parser.add_argument('--xml', action='store_true', help='xml output')
    args = parser.parse_args()

    if args.list:
        main_list(args.xml)
    elif args.suggest_new_devices:
        main_suggest(args.xml)
    elif args.register_device is not None:
        main_register_device(args.register_device)
    elif args.unregister_device is not None:
        main_unregister_device(args.unregister_device)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
