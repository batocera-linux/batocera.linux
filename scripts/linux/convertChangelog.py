#!/usr/bin/python3

# ./scripts/linux/convertChangelog.py < ./batocera-Changelog.md > changelog-content.html

from __future__ import annotations

import fileinput
import re
from typing import TypedDict


class _InfoDict(TypedDict):
    n: int
    level: int
    in_section: bool
    nitems: int
    nsubitems: int


def do_start_version(infos: _InfoDict, version: str | None, date: str | None, title: str | None, /) -> None:
    n = infos['n']
    if infos['level'] != 0:
        raise Exception("start of version doesn't start at level 0")
    infos['n'] = infos['n'] + 1
    infos['level'] = infos['level'] + 1

    strtitle = 'Batocera'
    if version is not None:
        strtitle = strtitle + ' ' + version
    if date is not None:
        strtitle = strtitle + ' - ' + date
    if title is not None:
        strtitle = strtitle + ' - ' + title

    if infos['n'] > 1:
        print('<br />')

    print('<div class="mb-4" id="accordion" role="tablist" aria-multiselectable="true">')
    print(' <div class="card">')
    print(f'  <div class="card-header" role="tab" id="heading{n}">')
    print('   <h5 class="mb-0">')
    print(
        f'    <a data-toggle="collapse" data-parent="#accordion" href="#collapse{n}" style="color:#2E2EFF" aria-expanded="true" aria-controls="collapse{n}" aria-label='
        f'>{strtitle}</a>'
    )
    print('   </h5>')
    print('  </div>')
    print(f'  <div id="collapse{n}" class="collapse')
    if n == 0:
        print(' show')
    print(f'" role="tabpanel" aria-labelledby="heading{n}">')
    print('   <div class="card-body">')


def do_end_version(infos: _InfoDict, /) -> None:
    print('  </div>')
    print(' </div>')
    print('</div>')

    infos['level'] = infos['level'] - 1
    if infos['level'] != 0:
        raise Exception("end of version doesn't end at level 0")


def do_start_section(line: str, /) -> None:
    print(f'   <b>{line}</b>')


def do_end_section() -> None:
    pass


def do_start_items() -> None:
    print('   <ul>')


def do_end_items() -> None:
    print('   </ul>')


def do_start_subitems() -> None:
    print('       <ul>')


def do_end_subitems() -> None:
    print('       </ul>')


def do_item(line: str, /) -> None:
    print(f'     <li>{line}</li>')


def do_subitem(line: str, /) -> None:
    print(f'         <li>{line}</li>')


def do_comment(line: str, /) -> None:
    print(f'<div>{line}</div>')


def read_changelog_line(infos: _InfoDict, line: str, /) -> None:
    # version
    m = re.search(r'^# (..../../..) - batocera\.linux', line)
    if m is not None:
        m = re.search(r'^# (..../../..) - batocera\.linux ([0-9\.]*) - (.*)$', line)
        if m is not None:
            vdate = m.group(1)
            vversion = m.group(2)
            vtitle = m.group(3)
        else:
            m = re.search(r'^# (..../../..) - batocera\.linux ([0-9\.]*)$', line)
            if m is not None:
                vdate = m.group(1)
                vversion = m.group(2)
                vtitle = None
            else:
                m = re.search(r'^# (..../../..) - batocera\.linux$', line)
                if m is not None:
                    vdate = m.group(1)
                    vversion = None
                    vtitle = None
                else:
                    raise Exception('invalid format ' + line)

        if infos['nsubitems'] > 0:
            infos['nsubitems'] = 0
            do_end_subitems()
        if infos['nitems'] > 0:
            infos['nitems'] = 0
            do_end_items()
        if infos['in_section']:
            do_end_section()
            infos['in_section'] = False
        do_start_version(infos, vversion, vdate, vtitle)
        return

    # end of version
    if line == '':
        if infos['nsubitems'] > 0:
            infos['nsubitems'] = 0
            do_end_subitems()
        if infos['nitems'] > 0:
            infos['nitems'] = 0
            do_end_items()
        if infos['in_section']:
            do_end_section()
            infos['in_section'] = False
        do_end_version(infos)
        return

    # section
    m = re.search(r'^### ([a-zA-Z].*)$', line)
    if m is not None:
        if infos['nsubitems'] > 0:
            infos['nsubitems'] = 0
            do_end_subitems()
        if infos['nitems'] > 0:
            infos['nitems'] = 0
            do_end_items()
        infos['in_section'] = True
        do_start_section(m.group(1))
        infos['nitems'] = 0
        return

    # item
    m = re.search(r'^- ([a-zA-Z0-9/"\*\.].*)$', line)
    if m is not None:
        if infos['nsubitems'] > 0:
            infos['nsubitems'] = 0
            do_end_subitems()
        if infos['nitems'] == 0:
            do_start_items()
            infos['nsubitems'] = 0
        do_item(m.group(1))
        infos['nitems'] = infos['nitems'] + 1
        return

    # subitem
    m = re.search(r'^  - ([a-zA-Z0-9/"\*\.].*)$', line)
    if m is not None:
        if infos['nsubitems'] == 0:
            do_start_subitems()
        do_subitem(m.group(1))
        infos['nsubitems'] = infos['nsubitems'] + 1
        return

    # comments
    m = re.search(r'^  ([a-zA-Z0-9/"\*~\.].*)$', line)
    if m is not None:
        do_comment(m.group(1))
        return

    raise Exception('invalid line : /' + line + '/')


def main() -> None:
    infos: _InfoDict = {'n': 0, 'level': 0, 'in_section': False, 'nitems': 0, 'nsubitems': 0}

    with fileinput.input() as f:
        for line in f:
            # print(line.strip("\n"))
            read_changelog_line(infos, line.strip('\n'))

    do_end_version(infos)


if __name__ == '__main__':
    main()
