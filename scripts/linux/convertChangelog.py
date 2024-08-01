#!/usr/bin/python3

# ./scripts/linux/convertChangelog.py < ./batocera-Changelog.md > changelog-content.html

import fileinput
import re

def do_startVersion(infos, version, date, title):
    n = infos["n"]
    if infos["level"] != 0:
        raise Exception("start of version doesn't start at level 0")
    infos["n"] = infos["n"]+1
    infos["level"] = infos["level"]+1

    strtitle = "Batocera"
    if version is not None:
        strtitle = strtitle + " " + version
    if date is not None:
        strtitle = strtitle + " - " + date
    if title is not None:
        strtitle = strtitle + " - " + title

    if infos["n"] > 1:
        print("<br />")
    
    print("<div class=\"mb-4\" id=\"accordion\" role=\"tablist\" aria-multiselectable=\"true\">")
    print(" <div class=\"card\">")
    print("  <div class=\"card-header\" role=\"tab\" id=\"heading{}\">".format(n))
    print("   <h5 class=\"mb-0\">")
    print("    <a data-toggle=\"collapse\" data-parent=\"#accordion\" href=\"#collapse{}\" style=\"color:#2E2EFF\" aria-expanded=\"true\" aria-controls=\"collapse{}\" aria-label="">{}</a>".format(n, n, strtitle))
    print("   </h5>")
    print("  </div>")
    print("  <div id=\"collapse{}\" class=\"collapse".format(n))
    if n== 0:
        print(" show")      
    print("\" role=\"tabpanel\" aria-labelledby=\"heading{}\">".format(n))
    print("   <div class=\"card-body\">")

def do_endVersion(infos):
    print("  </div>")
    print(" </div>")
    print("</div>")
    
    infos["level"] = infos["level"]-1
    if infos["level"] != 0:
        raise Exception("end of version doesn't end at level 0")

def do_start_section(line):
    print("   <b>{}</b>".format(line))

def do_end_section():
    pass

def do_start_items():
    print("   <ul>")

def do_end_items():
    print("   </ul>")

def do_start_subitems():
    print("       <ul>")

def do_end_subitems():
    print("       </ul>")

def do_item(line):
    print("     <li>{}</li>".format(line))

def do_subitem(line):
    print("         <li>{}</li>".format(line))
    
def do_comment(line):
    print("<div>{}</div>".format(line))

def readChangeLogLine(infos, line):
    # version
    m = re.search('^# (..../../..) - batocera\.linux', line)
    if m is not None:
        m = re.search('^# (..../../..) - batocera\.linux ([0-9\.]*) - (.*)$', line)
        if m is not None:
            vdate    = m.group(1)
            vversion = m.group(2)
            vtitle   = m.group(3)
        else:
            m = re.search('^# (..../../..) - batocera\.linux ([0-9\.]*)$', line)
            if m is not None:
                vdate    = m.group(1)
                vversion = m.group(2)
                vtitle   = None
            else:
                m = re.search('^# (..../../..) - batocera\.linux$', line)
                if m is not None:
                    vdate    = m.group(1)
                    vversion = None
                    vtitle   = None
                else:
                    raise Exception("invalid format " + line)
        
        if infos["nsubitems"] > 0:
            infos["nsubitems"] = 0
            do_end_subitems()
        if infos["nitems"] > 0:
            infos["nitems"] = 0
            do_end_items()
        if infos["in_section"]:
            do_end_section()
            infos["in_section"] = False
        do_startVersion(infos, vversion, vdate, vtitle);
        return

    # end of version
    if line == "":
        if infos["nsubitems"] > 0:
            infos["nsubitems"] = 0
            do_end_subitems()
        if infos["nitems"] > 0:
            infos["nitems"] = 0
            do_end_items()
        if infos["in_section"]:
            do_end_section()
            infos["in_section"] = False
        do_endVersion(infos)
        return

    # section
    m = re.search('^### ([a-zA-Z].*)$', line)
    if m is not None:
        if infos["nsubitems"] > 0:
            infos["nsubitems"] = 0
            do_end_subitems()
        if infos["nitems"] > 0:
            infos["nitems"] = 0
            do_end_items()
        infos["in_section"] = True
        do_start_section(m.group(1))
        infos["nitems"] = 0
        return

    # item
    m = re.search('^- ([a-zA-Z0-9/"\*\.].*)$', line)
    if m is not None:
        if infos["nsubitems"] > 0:
            infos["nsubitems"] = 0
            do_end_subitems()
        if infos["nitems"] == 0:
            do_start_items()
            infos["nsubitems"] = 0
        do_item(m.group(1))
        infos["nitems"] = infos["nitems"] + 1
        return

    # subitem
    m = re.search('^  - ([a-zA-Z0-9/"\*\.].*)$', line)
    if m is not None:
        if infos["nsubitems"] == 0:
            do_start_subitems()
        do_subitem(m.group(1))
        infos["nsubitems"] = infos["nsubitems"] + 1
        return

    # comments
    m = re.search('^  ([a-zA-Z0-9/"\*\.].*)$', line)
    if m is not None:
        do_comment(m.group(1))
        return

    raise Exception("invalid line : /" + line + "/")

infos = { "n": 0, "level": 0, "in_section": False, "nitems": 0, "nsubitems": 0}
for line in fileinput.input():
    #print(line.strip("\n"))
    readChangeLogLine(infos, line.strip("\n"))
do_endVersion(infos)
