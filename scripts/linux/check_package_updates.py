#!/usr/bin/env python3
import os
import sys
import re
import json
import urllib.request
import urllib.error
import urllib.parse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- COLORS ---
RESET = "\033[0m"
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
PINK = "\033[1;35m"
BOLD = "\033[1m"

# --- DEBUG ---
# Set CHECK_PKG_DEBUG=1 to print the resolved SITE/BRANCH/VERSION for each
# package right before routing, and to stop silencing fetch failures.
_DEBUG = os.environ.get("CHECK_PKG_DEBUG") == "1"


# --- GROUPS ---
GROUPS = {
    "RETROARCH": [
        "retroarch", "retroarch-assets", "libretro-core-info", "batocera-bezel",
        "batocera-shaders", "common-shaders", "glsl-shaders", "slang-shaders"
    ],
    "LIBRETRO": [
        "libretro-81", "libretro-arduous", "libretro-atari800", "libretro-beetle-lynx",
        "libretro-beetle-ngp", "libretro-beetle-pce", "libretro-beetle-pce-fast",
        "libretro-beetle-pcfx", "libretro-beetle-psx", "libretro-beetle-saturn",
        "libretro-beetle-supergrafx", "libretro-beetle-vb", "libretro-beetle-wswan",
        "libretro-blastem", "libretro-bluemsx", "libretro-boom3", "libretro-bsnes",
        "libretro-bsnes-hd", "libretro-cap32", "libretro-chailove", "libretro-craft",
        "libretro-desmume", "libretro-dinothawr", "libretro-dolphin", "libretro-dosbox-pure",
        "libretro-easyrpg", "libretro-ecwolf", "libretro-emuscv", "libretro-fake08",
        "libretro-fbalpha", "libretro-fbneo", "libretro-fceumm", "libretro-flycast",
        "libretro-fmsx", "libretro-freechaf", "libretro-freeintv", "libretro-fuse",
        "libretro-gambatte", "libretro-gearsystem", "libretro-genesisplusgx",
        "libretro-genesisplusgx-expanded", "libretro-genesisplusgx-wide", "libretro-gpsp",
        "libretro-gw", "libretro-handy", "libretro-hatari", "libretro-hatarib",
        "libretro-imame", "libretro-kronos", "libretro-lowresnx", "libretro-lutro",
        "libretro-mame", "libretro-mame2003-plus", "libretro-melonds", "libretro-melonds-ds",
        "libretro-mesen", "libretro-mesens", "libretro-mgba", "libretro-minivmac",
        "libretro-mrboom", "libretro-mupen64plus-next", "libretro-neocd", "libretro-nestopia",
        "libretro-nxengine", "libretro-o2em", "libretro-opera", "libretro-parallel-n64",
        "libretro-pc88", "libretro-pc98", "libretro-pcsx", "libretro-picodrive",
        "libretro-pocketsnes", "libretro-pokemini", "libretro-ppsspp", "libretro-prboom",
        "libretro-prosystem", "libretro-puae", "libretro-px68k", "libretro-reminiscence",
        "libretro-same-cdi", "libretro-sameduck", "libretro-scummvm", "libretro-smsplus-gx",
        "libretro-snes9x", "libretro-snes9x-next", "libretro-stella", "libretro-stella2014",
        "libretro-superbroswar", "libretro-superflappybirds", "libretro-swanstation",
        "libretro-tgbdual", "libretro-theodore", "libretro-tic80", "libretro-tyrquake",
        "libretro-uae4arm", "libretro-uzem", "libretro-vba-m", "libretro-vecx",
        "libretro-vemulator", "libretro-vice", "libretro-virtualjaguar", "libretro-vitaquake2",
        "libretro-wasm4", "libretro-watara", "libretro-xmil", "libretro-xrick",
        "libretro-yabasanshiro", "libretro-zc210"
    ],
    "MUPEN": [
        "mupen64plus-audio-sdl", "mupen64plus-core", "mupen64plus-gliden64",
        "mupen64plus-input-sdl", "mupen64plus-rsp-hle", "mupen64plus-ui-console",
        "mupen64plus-video-glide64mk2", "mupen64plus-video-rice"
    ],
    "OPENBOR": [
        "openbor4432", "openbor6330", "openbor6412", "openbor6510", "openbor7142", "openbor7530"
    ],
    "EMULATORS": [
        "amiberry", "applewin", "azahar", "bigpemu", "cemu", "clk",
        "hypseus-singe", "dolphin-emu", "dosbox", "dosbox-staging", "dosbox-x",
        "duckstation", "easyrpg-player", "liblcf", "eka2l1", "flycast", "fsuae",
        "gsplus", "hatari", "ikemen", "lexaloffle-pico8", "lexaloffle-voxatron",
        "lightspark", "mame", "melonds", "model2", "openmsx", "pcsx2", "pifba",
        "ppsspp", "python-pygame2", "python-pyxel", "redream", "rpcs3", "ruffle",
        "ryujinx", "scummvm", "shadps4", "simcoupe", "snes9x", "solarus-engine",
        "sugarbox", "supermodel", "supermodel-es", "thextech", "tsugaru", "vice",
        "vita3k", "vpinball", "x16emu", "xemu", "xemu", "xenia", "xenia-canary"
    ],
    "PORTS": [
        "abuse", "abuse-data", "bloodmod", "bstone", "cannonball", "catacombgl",
        "cdogs", "cdoom", "cgenius", "corsixth", "d3le", "dentonmod", "desolated",
        "devilutionx", "dhewm3", "dxx-rebirth", "ecwolf", "eduke32", "eldoom",
        "etlegacy", "fallout1-ce", "fallout2-ce", "fheroes2", "fitz", "grimm",
        "gzdoom", "hardcorps", "hcl", "hurrican", "ioquake3", "iortcw", "jazz2-native",
        "lindbergh-loader", "openmohaa", "openjazz", "openjk", "openjkdf2", "perfected",
        "raze", "realgibs", "rivensin", "sdlpop", "sikkmod", "sonic3-air", "sonic2013",
        "soniccd", "sonic-mania", "taradino", "theforceengine", "trx", "tyrian",
        "uqm", "vcmi", "hlsdk-xash3d", "hlsdk-xash3d-dmc", "hlsdk-xash3d-opfor",
        "xash3d-fwgs", "vkquake", "vkquake2", "vkquake3", "yquake2", "yquake2-xatrix",
        "yquake2-rogue", "yquake2-zaero"
    ],
    "WINE": [
        "dxvk", "dxvk-nvapi", "faudio", "mf", "rtkit", "vkd3d-proton", "wine-tkg"
    ],
    "CONTROLLERS": [
        "aelightgun", "aimtrak-guns", "anbernic-gpio-pad", "batocera-gun-calibrator",
        "batocera-wheel-calibrator", "db9_gpio_rpi", "dolphinbar-guns", "dolphinCrosshairsPack",
        "fun-r1-gamepad", "fusion-lightguns", "gamecon_gpio_rpi", "gun4ir-guns", "guncon",
        "guncon3", "hid-nx", "input-wrapper", "joycond", "lightguns-games-precalibrations",
        "mk_arcade_joystick_rpi", "new-lg4ff", "openfire-guns", "onehit-guns", "qtsixa",
        "qtsixa-shanwan", "retrogame", "retroshooter-guns", "samco-guns", "sinden-guns",
        "sinden-guns-libs", "steamdeckgun", "uinput-joystick", "umtool", "wiimote-3rdparty",
        "wiimotes-rules", "xarcade2jstick", "xgunner-lightguns", "xone", "xow", "xpadneo",
        "xpad-noone"
    ],
    "WINE": [
        "dxvk", "dxvk-nvapi", "faudio", "mf", "rtkit", "vkd3d-proton", "wine-tkg"
    ],
    "UTILS": [
        "box64", "btop", "mangohud", "moonlight-embedded", "moonlight-qt", "ryzenadj",
        "switchres", "syncthing", "winetricks"
    ]
}


# --- WEB HELPERS ---
def fetch_url(url, as_json=False, silent=False):
    """Utility to perform safe HTTP requests. Falls back to system curl and wget
    to bypass Cloudflare checks."""
    if _DEBUG:
        silent = False

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            data = response.read()
            decoded = data.decode('utf-8', errors='ignore')
            if as_json:
                try:
                    return json.loads(decoded)
                except json.JSONDecodeError:
                    if "Making sure you're not a bot" in decoded or "within.website" in decoded:
                        if not silent or _DEBUG:
                            print(f"[Debug] Blocked by anti-bot challenge (Anubis) for {url}",
                                  file=sys.stderr)
                        return {"__blocked__": "anubis"}
                    if _DEBUG:
                        snippet = decoded[:300].replace("\n", " ")
                        print(f"[DEBUG] Non-JSON response for {url}: {snippet!r}",
                              file=sys.stderr)
                    return None
            return decoded
    except urllib.error.HTTPError as e:
        if not silent:
            print(f"[Debug] HTTP {e.code} for {url}", file=sys.stderr)
    except Exception as e:
        if _DEBUG:
            print(f"[DEBUG] urllib exception for {url}: {type(e).__name__}: {e}",
                  file=sys.stderr)

    try:
        res = subprocess.run(
            ["curl", "-L", "-s", "-m", "12", "-A", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36", url],
            capture_output=True, text=True, errors="ignore"
        )
        if res.returncode == 0 and res.stdout:
            if as_json:
                try:
                    return json.loads(res.stdout)
                except json.JSONDecodeError:
                    if _DEBUG:
                        snippet = res.stdout[:300].replace("\n", " ")
                        print(f"[DEBUG] curl fallback non-JSON for {url}: {snippet!r}",
                              file=sys.stderr)
                    return None
            return res.stdout
        elif _DEBUG:
            print(f"[DEBUG] curl fallback rc={res.returncode} stderr={res.stderr[:200]!r} for {url}",
                  file=sys.stderr)
    except Exception as e:
        if _DEBUG:
            print(f"[DEBUG] curl fallback exception for {url}: {type(e).__name__}: {e}",
                  file=sys.stderr)

    try:
        res = subprocess.run(
            ["wget", "-qO", "-", "-T", "12", "-U", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36", url],
            capture_output=True, text=True, errors="ignore"
        )
        if res.returncode == 0 and res.stdout:
            if as_json:
                try:
                    return json.loads(res.stdout)
                except json.JSONDecodeError:
                    if _DEBUG:
                        snippet = res.stdout[:300].replace("\n", " ")
                        print(f"[DEBUG] wget fallback non-JSON for {url}: {snippet!r}",
                              file=sys.stderr)
                    return None
            return res.stdout
        elif _DEBUG:
            print(f"[DEBUG] wget fallback rc={res.returncode} stderr={res.stderr[:200]!r} for {url}",
                  file=sys.stderr)
    except Exception as e:
        if _DEBUG:
            print(f"[DEBUG] wget fallback exception for {url}: {type(e).__name__}: {e}",
                  file=sys.stderr)

    if not silent:
        print(f"[Debug] Fetch completely failed for {url}", file=sys.stderr)
    return None


# --- SCRAPERS / API LOGIC ---

def github_commit_info(repo, commit_sha):
    # API only for fast dates. No recursive HTML scraper fallback to avoid rate-limiting blocks.
    api_url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and isinstance(res, dict) and "commit" in res and "author" in res["commit"]:
        date = res["commit"]["author"].get("date", "")
        if date:
            return date.split("T")[0]
    return ""


def github_latest_commit(repo, branch=None):
    """Fetches latest commit SHA and date directly in one network request."""
    # Tier 1: Try GitHub REST API
    api_url = f"https://api.github.com/repos/{repo}/commits"
    api_url += f"?sha={branch}&per_page=1" if branch else "?per_page=1"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and isinstance(res, list) and len(res) > 0:
        sha = res[0].get("sha", "")
        date = res[0].get("commit", {}).get("author", {}).get("date", "")
        if date:
            date = date.split("T")[0]
        return sha, date

    # Tier 2: Fallback to RSS/Atom feeds (Extract both SHA and Date from the same feed response)
    branches_to_try = [branch] if branch else ["main", "master", "next", "devel"]
    for br in branches_to_try:
        url_atom = f"https://github.com/{repo}/commits/{br}.atom"
        html_atom = fetch_url(url_atom, silent=True)
        if html_atom:
            m_entry = re.search(r'<entry>(.*?)</entry>', html_atom, re.DOTALL)
            if m_entry:
                entry_content = m_entry.group(1)
                sha_match = re.search(r'Commit/([0-9a-f]{40})', entry_content) or re.search(r'/commit/([0-9a-f]{40})', entry_content)
                if sha_match:
                    sha = sha_match.group(1)
                    date_match = re.search(r'<(?:updated|published)>([^<]+)', entry_content)
                    date = date_match.group(1).split("T")[0].strip() if date_match else ""
                    return sha, date

    # Tier 3: Fallback to HTML scraping (Extract SHA only)
    url_html = f"https://github.com/{repo}/commits"
    if branch:
        url_html += f"/{branch}"
    html_page = fetch_url(url_html, silent=True)
    if html_page:
        m = re.search(r'/commit/([0-9a-f]{40})', html_page)
        if m:
            return m.group(1), ""
    return "", ""


def github_tag_info(repo, tag):
    # API only. No recursive fallback.
    api_url = f"https://api.github.com/repos/{repo}/commits/{tag}"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and isinstance(res, dict) and "commit" in res and "author" in res["commit"]:
        date = res["commit"]["author"].get("date", "")
        if date:
            return date.split("T")[0]
    return ""


def github_latest_tag(repo):
    """Fetches the latest release/tag and date using chronological Atom feeds (immune to REST tag alphabetization)."""
    # Tier 1: Try the Atom tags feed (Extract both Tag and Date from the first entry block)
    html_atom = fetch_url(f"https://github.com/{repo}/tags.atom", silent=True)
    if html_atom:
        m_entry = re.search(r'<entry>(.*?)</entry>', html_atom, re.DOTALL)
        if m_entry:
            entry_content = m_entry.group(1)
            tag_match = re.search(r'/releases/tag/([^"/<>#\s?]+)', entry_content)
            if tag_match:
                tag = tag_match.group(1)
                date_match = re.search(r'<(?:updated|published)>([^<]+)', entry_content)
                date = date_match.group(1).split("T")[0].strip() if date_match else ""
                return tag, date

            titles = re.findall(r'<title[^>]*>([^<]+)</title>', entry_content)
            if titles:
                tag = titles[0].strip()
                date_match = re.search(r'<(?:updated|published)>([^<]+)', entry_content)
                date = date_match.group(1).split("T")[0].strip() if date_match else ""
                return tag, date

    # Tier 2: Try the Atom releases feed
    html_rel = fetch_url(f"https://github.com/{repo}/releases.atom", silent=True)
    if html_rel:
        m_entry = re.search(r'<entry>(.*?)</entry>', html_rel, re.DOTALL)
        if m_entry:
            entry_content = m_entry.group(1)
            tag_match = re.search(r'/releases/tag/([^"/<>#\s?]+)', entry_content)
            if tag_match:
                tag = tag_match.group(1)
                date_match = re.search(r'<(?:updated|published)>([^<]+)', entry_content)
                date = date_match.group(1).split("T")[0].strip() if date_match else ""
                return tag, date

    # Tier 3: Fallback to HTML tags page
    html_page = fetch_url(f"https://github.com/{repo}/tags", silent=True)
    if html_page:
        matches = re.findall(r'/releases/tag/([^"/<>#\s?]+)', html_page)
        for m in matches:
            if m != "latest":
                return m, ""
    return "", ""


def github_latest_tag_filtered(repo, pattern_str):
    pattern = re.compile(pattern_str)

    # Try API Speculatively
    api_url = f"https://api.github.com/repos/{repo}/tags?per_page=10"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and isinstance(res, list):
        for t in res:
            name = t.get("name", "")
            if pattern.search(name):
                sha = t.get("commit", {}).get("sha", "")
                date = github_commit_info(repo, sha) if sha else ""
                return name, date

    # Check Atom tags feed
    html_atom = fetch_url(f"https://github.com/{repo}/tags.atom", silent=True)
    if html_atom:
        entries = re.findall(r'<entry>(.*?)</entry>', html_atom, re.DOTALL)
        for entry_content in entries:
            tag_match = re.search(r'/releases/tag/([^"/<>#\s?]+)', entry_content)
            if tag_match and pattern.search(tag_match.group(1)):
                tag = tag_match.group(1)
                date_match = re.search(r'<(?:updated|published)>([^<]+)', entry_content)
                date = date_match.group(1).split("T")[0].strip() if date_match else ""
                return tag, date

            titles = re.findall(r'<title[^>]*>([^<]+)</title>', entry_content)
            if titles and pattern.search(titles[0]):
                tag = titles[0].strip()
                date_match = re.search(r'<(?:updated|published)>([^<]+)', entry_content)
                date = date_match.group(1).split("T")[0].strip() if date_match else ""
                return tag, date

    # Fallback HTML scraping
    html_page = fetch_url(f"https://github.com/{repo}/tags", silent=True)
    if html_page:
        matches = re.findall(r'/releases/tag/([^"/<>#\s?]+)', html_page)
        for m in matches:
            if pattern.search(m):
                return m, ""
    return "", ""


def gitlab_commit_info(repo, sha):
    encoded = urllib.parse.quote_plus(repo)
    api_url = f"https://gitlab.com/api/v4/projects/{encoded}/repository/commits/{sha}"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and "committed_date" in res:
        return res["committed_date"].split("T")[0]
    return ""


def gitlab_latest_commit(repo, branch=None):
    encoded = urllib.parse.quote_plus(repo)
    api_url = f"https://gitlab.com/api/v4/projects/{encoded}/repository/commits"
    api_url += f"?ref_name={branch}&per_page=1" if branch else "?per_page=1"

    res = fetch_url(api_url, as_json=True, silent=True)
    if res and isinstance(res, list) and len(res) > 0:
        sha = res[0].get("id", "")
        date = res[0].get("committed_date", "")
        if date:
            date = date.split("T")[0]
        return sha, date

    # Fallback HTML
    url = f"https://gitlab.com/{repo}/-/commits"
    url += f"/{branch}/?ref_type=HEADS" if branch else "/?ref_type=HEADS"
    html = fetch_url(url, silent=True)
    if html:
        m = re.search(r'/commit/([0-9a-f]{40})', html)
        if m:
            return m.group(1), ""
    return "", ""


def gitlab_latest_tag(repo):
    encoded = urllib.parse.quote_plus(repo)
    api_url = f"https://gitlab.com/api/v4/projects/{encoded}/repository/tags?per_page=1"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and isinstance(res, list) and len(res) > 0:
        tag = res[0].get("name", "")
        date = res[0].get("commit", {}).get("committed_date", "")
        if date:
            date = date.split("T")[0]
        return tag, date

    # Fallback HTML
    html = fetch_url(f"https://gitlab.com/{repo}/-/tags", silent=True)
    if html:
        m = re.search(r'/-/tags/([^"/]+)', html)
        if m:
            return m.group(1), ""
    return "", ""


def gitlab_tag_info(repo, tag):
    encoded = urllib.parse.quote_plus(repo)
    api_url = f"https://gitlab.com/api/v4/projects/{encoded}/repository/tags/{tag}"
    res = fetch_url(api_url, as_json=True, silent=True)
    if res and "commit" in res:
        date = res["commit"].get("committed_date", "")
        if date:
            return date.split("T")[0]
    return ""


# --- SPECIALIZED WEBSITES ---

def richwhitehouse_latest():
    html = fetch_url('https://www.richwhitehouse.com/jaguar/index.php?content=download')
    if html:
        m = re.search(r'BigPEmu_Linux64_(v[0-9]*)\.tar\.gz', html)
        if m:
            return m.group(1)
    return ""


def redream_latest():
    html = fetch_url('https://redream.io/download')
    if html:
        m = re.search(r'universal-raspberry-linux-v(.*?).tar', html)
        if m:
            return m.group(1)
    return ""


def sourceforge_latest(project_path="vice-emu/files/releases/"):
    html = fetch_url(f'https://sourceforge.net/projects/{project_path}')
    if html:
        m = re.search(r'vice-([^\s/]+?)\.tar', html)
        if m:
            return m.group(1)
    return ""


def abusedata_latest():
    html = fetch_url('http://abuse.zoy.org/raw-attachment/wiki/download')
    if html:
        m = re.search(r'abuse-data-(.*?)\.tar', html)
        if m:
            return m.group(1)
    return ""


def voidpoint_latest_commit(repo, branch=None):
    url = f"https://voidpoint.io/{repo}/-/commits"
    if branch:
        url += f"/{branch}"
    html = fetch_url(url)
    sha = ""
    if html:
        m = re.search(r'/commit/([0-9a-f]{40})', html)
        if m:
            sha = m.group(1)
    date = ""
    if sha:
        html_c = fetch_url(f"https://voidpoint.io/{repo}/-/commit/{sha}")
        if html_c:
            m_d = re.search(r'data-container="body">([^<]+)</time>', html_c)
            if m_d:
                date = m_d.group(1)
    return sha, date


def winehqgit_latest_commit(repo):
    html = fetch_url(f"https://source.winehq.org/git/{repo}")
    sha = ""
    if html:
        m = re.search(r'/commit/([0-9a-f]{40})', html)
        if m:
            sha = m.group(1)
    date = ""
    if sha:
        html_c = fetch_url(f"https://source.winehq.org/git/{repo}/commit/{sha}")
        if html_c:
            m_d = re.search(r'datetime">([^<]+)', html_c)
            if m_d:
                date_str = m_d.group(1)
                m_date = re.match(r'.*?,\s*(\S+)\s+(\S+)\s+(\S+)', date_str)
                if m_date:
                    date = f"{m_date.group(2)} {m_date.group(1)}, {m_date.group(3)}"
                else:
                    date = date_str
    return sha, date


def winehqgit_latest_tag(repo):
    html = fetch_url(f"https://source.winehq.org/git/{repo}/tags")
    tag = ""
    if html:
        m = re.search(r'class="list name".*?>(.*?)</a>', html)
        if m:
            tag = m.group(1)
    date = ""
    if tag:
        html_tags = fetch_url(f"https://source.winehq.org/git/{repo}/tags")
        if html_tags:
            for line in html_tags.splitlines():
                if tag in line:
                    m_c = re.search(r'/commit/([0-9a-f]{40})', line)
                    if m_c:
                        sha = m_c.group(1)
                        html_c = fetch_url(f"https://source.winehq.org/git/{repo}/commit/{sha}")
                        if html_c:
                            m_d = re.search(r'datetime">([^<]+)', html_c)
                            if m_d:
                                date_str = m_d.group(1)
                                m_date = re.match(r'.*?,\s*(\S+)\s+(\S+)\s+(\S+)', date_str)
                                if m_date:
                                    date = f"{m_date.group(2)} {m_date.group(1)}, {m_date.group(3)}"
                        break
    return tag, date


def winehqdl_latest(path):
    html = fetch_url(f"https://dl.winehq.org/{path}/")
    tag = ""
    if html:
        dirs = re.findall(r'href="([^"]+)/"', html)
        if dirs:
            tag = dirs[-1]
    date = ""
    if tag and html:
        for line in html.splitlines():
            if tag in line:
                m = re.search(r'mod">([^<]+?)\s+\d+:\d+', line)
                if m:
                    date = m.group(1).strip()
                    break
    return tag, date


def sinden_lightgun_latest():
    html = fetch_url('https://sindenlightgun.com/drivers/')
    if html:
        m = re.search(r'ReleaseV([^"\s]+?)\.zip', html)
        if m:
            return m.group(1)
    return ""


def kodi_resources_latest(url):
    html = fetch_url(url)
    if html:
        zips = re.findall(r'-([^-]+?)\.zip', html)
        if zips:
            return zips[-1]
    return ""


def uboot_multiboard_latest(url):
    html = fetch_url(url)
    if html:
        links = re.findall(r'u-boot-([^\s<>]+?)\.tar\.bz2', html)
        non_rc = [l for l in links if "-rc" not in l]
        if non_rc:
            return non_rc[-1]
    return ""


def initramfs_latest(url):
    html = fetch_url(url)
    if html:
        links = re.findall(r'busybox-([^\s<>"]+?)\.tar\.bz2', html)
        if links:
            return links[-1]
    return ""


def shim_signed_efi_ia32_latest(url):
    html = fetch_url(url)
    if html:
        links = re.findall(r'_([^\s<>"]+?)_i386\.deb', html)
        non_deb = [l for l in links if "~deb" not in l]
        if non_deb:
            return non_deb[-1]
    return ""


def shim_signed_efi_x64_latest():
    html = fetch_url("https://packages.ubuntu.com/search?keywords=shim-signed&searchon=names")
    if html:
        matches = re.findall(r'<br>([^:]+?):', html)
        filtered = [m for m in matches if "-0ubuntu1" in m]
        if filtered:
            return filtered[-1]
    return ""


def hatari_latest(url):
    html = fetch_url(url)
    tag = ""
    if html:
        m = re.search(r'hatari-([^\s<>"]+?)\.tar\.gz', html)
        if m:
            tag = m.group(1)
    date = ""
    if tag:
        html_t = fetch_url(f"{url}/tag/?id=v{tag}")
        if html_t:
            m_d = re.search(r'tag date</td><td>([^<]+?)\s+\d+:\d+', html_t)
            if m_d:
                date = m_d.group(1).strip()
    return tag, date

def all_linux_firmware_latest(url):
    html = fetch_url(url)
    if html:
        m = re.search(r'linux-firmware-([^\s<>"]+?)\.tar\.gz', html)
        if m:
            return m.group(1)
    return ""


def mesa3d_latest():
    html = fetch_url("https://archive.mesa3d.org/")
    if html:
        links = re.findall(r'mesa-([^\s<>"]+?)\.tar\.xz', html)
        non_rc = [l for l in links if "-rc" not in l]
        if non_rc:
            return non_rc[-1]
    return ""


def nvidia_latest():
    html = fetch_url("https://download.nvidia.com/XFree86/Linux-x86_64/")
    if html:
        versions = re.findall(r'href="(\d+\.\d+(?:\.\d+)*)/?"', html)
        if versions:
            def parse_ver(v):
                try:
                    return [int(x) for x in v.split(".")]
                except ValueError:
                    return [0]
            versions.sort(key=parse_ver)
            return versions[-1]
    return ""


def python_hosted_latest(pkg):
    name = pkg.split('-', 1)[-1] if '-' in pkg else pkg
    html = fetch_url(f"https://pypi.org/project/{name}/")
    if html:
        m = re.search(r'href="[^"]*?/packages/.*?/.*?/' + re.escape(name) + r'-([0-9.]+)\.tar\.gz"', html, re.IGNORECASE)
        if m:
            return m.group(1)
        m2 = re.search(re.escape(name) + r'-([0-9.]+)\.tar\.gz', html, re.IGNORECASE)
        if m2:
            return m2.group(1)
    return ""


def kyroflux_latest(pkg):
    if pkg == "libcapsimage":
        html = fetch_url("https://www.kryoflux.com/?page=download")
        if html:
            m = re.search(r'spsdeclib_(.*?)_source\.zip', html)
            if m:
                return m.group(1)
    return ""


def libenet_latest():
    html = fetch_url("http://enet.bespin.org/Downloads.html")
    if html:
        m = re.search(r'download/enet-(.*?)\.tar\.gz', html)
        if m:
            return m.group(1)
    return ""


def jpegsrc_latest():
    html = fetch_url("https://www.ijg.org/files/")
    if html:
        matches = re.findall(r'jpegsrc\.v([^\s<>"]+?)\.tar\.gz', html)
        if matches:
            return matches[-1]
    return ""


def libopenmpt_latest():
    html = fetch_url("https://lib.openmpt.org/files/libopenmpt/src/")
    if html:
        matches = re.findall(r'libopenmpt-([^\s<>"]+?)\+release\.autotools\.tar\.gz', html)
        if matches:
            return matches[-1]
    return ""


def uqm_latest():
    html = fetch_url("https://sourceforge.net/p/sc2/uqm/ci/main/tree/")
    if html:
        m = re.search(r'/p/sc2/uqm/ci/([0-9a-f]{40})', html)
        if m:
            return m.group(1)
    return ""


def linaro_latest():
    html = fetch_url("https://releases.linaro.org/components/toolchain/binaries/")
    if html:
        matches = re.findall(r'/binaries/([^"/]+)/', html)
        if matches:
            return matches[-1]
    return ""


def cabextract_latest():
    html = fetch_url("https://www.cabextract.org.uk/")
    if html:
        m = re.search(r'cabextract-(.*?)\.tar\.gz', html)
        if m:
            return m.group(1)
    return ""


def pacman_latest():
    html = fetch_url("https://sources.archlinux.org/other/pacman/")
    if html:
        matches = re.findall(r'pacman-(.*?)\.tar', html)
        if matches:
            return matches[-1]
    return ""


def pmutils_latest():
    html = fetch_url("https://pm-utils.freedesktop.org/releases/")
    if html:
        matches = re.findall(r'pm-utils-(.*?)\.tar\.gz', html)
        if matches:
            return matches[-1]
    return ""


def gitlab_freedesktop_latest_tag(repo):
    """Uses freedesktop GitLab REST API directly to retrieve tags securely without Cloudflare blocks."""
    encoded = urllib.parse.quote_plus(repo)
    api_url = f"https://gitlab.freedesktop.org/api/v4/projects/{encoded}/repository/tags?per_page=1"
    res = fetch_url(api_url, as_json=True, silent=True)
    if isinstance(res, dict) and res.get("__blocked__") == "anubis":
        return "BLOCKED-BY-ANTIBOT", ""
    if res and isinstance(res, list) and len(res) > 0:
        tag = res[0].get("name", "")
        date = res[0].get("commit", {}).get("committed_date", "")
        if date:
            date = date.split("T")[0]
        return tag, date

    # Tier 2: Fallback to HTML parsing
    html = fetch_url(f"https://gitlab.freedesktop.org/{repo}/-/tags", silent=True)
    tag = ""
    if html:
        m = re.search(r'/-/tags/([^"/#?\s]+)', html)
        if m:
            tag = m.group(1)
    return tag, ""


def floodgap_xa_latest():
    html = fetch_url("https://www.floodgap.com/retrotech/xa/dists/")
    if html:
        matches = re.findall(r'xa-(.*?)\.tar\.gz', html)
        if matches:
            return matches[-1]
    return ""


def adwaita_icon_theme_latest():
    html_parent = fetch_url("https://download.gnome.org/sources/adwaita-icon-theme/")
    if html_parent:
        matches_dir = re.findall(r'>([0-9.]+)/<', html_parent)
        if matches_dir:
            latest_dir = matches_dir[-1]
            html_sub = fetch_url(f"https://download.gnome.org/sources/adwaita-icon-theme/{latest_dir}/")
            if html_sub:
                matches_tar = re.findall(r'adwaita-icon-theme-([0-9.]+)\.tar', html_sub)
                if matches_tar:
                    return matches_tar[-1]
    return ""


def sourcehut_latest_tag(repo):
    html = fetch_url(f"https://git.sr.ht/{repo}/refs/")
    tag = ""
    if html:
        m = re.search(r'archive/(.*?)\.tar', html)
        if m:
            tag = m.group(1)
    date = ""
    if tag:
        html_t = fetch_url(f"https://git.sr.ht/{repo}/refs/{tag}")
        if html_t:
            m_d = re.search(r'datetime="([^"]+?)"[^>]*>.*?UTC', html_t)
            if m_d:
                date = m_d.group(1)
    return tag, date


# --- BUILDROOT FILE PARSING LOGIC ---

def find_mk_file(pkg_name):
    """Recursively walks down ./package/batocera to look for package_name.mk."""
    search_path = os.path.join("package", "batocera")
    if not os.path.isdir(search_path):
        search_path = "./package"

    if os.path.isdir(search_path):
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.lower() == f"{pkg_name}.mk".lower():
                    return os.path.join(root, file)
    return None


def parse_mk_properties(pkg_name):
    """Parses SITE, VERSION, and BRANCH properties safely, including resolving any nested macro variables like $(VAR)."""
    mk_file = find_mk_file(pkg_name)
    if not mk_file:
        return None

    with open(mk_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Resolve Buildroot multiline backslashes '\'
    lines = content.splitlines()
    joined_lines = []
    current_line = ""
    for line in lines:
        if line.endswith("\\"):
            current_line += line[:-1].strip() + " "
        else:
            current_line += line.strip()
            joined_lines.append(current_line)
            current_line = ""
    if current_line:
        joined_lines.append(current_line)

    variables = {}
    for line in joined_lines:
        if line.startswith("#") or "=" not in line:
            continue
        parts = line.split("=", 1)
        var_name = parts[0].strip()
        if var_name.endswith("+") or var_name.endswith("?") or var_name.endswith(":"):
            var_name = var_name[:-1].strip()

        if re.match(r"^[A-Z0-9_]+$", var_name):
            val = parts[1].strip()
            variables[var_name] = val

    def resolve_macros(val, depth=0):
        if depth > 10:
            return val
        matches = re.findall(r"\$\(([^)]+)\)", val)
        if not matches:
            return val
        for m in matches:
            if m in variables:
                resolved_m = resolve_macros(variables[m], depth + 1)
                val = val.replace(f"$({m})", resolved_m)
        return val

    var_prefix = pkg_name.replace("-", "_").upper()
    version = variables.get(f"{var_prefix}_VERSION")
    site = variables.get(f"{var_prefix}_SITE")
    branch = variables.get(f"{var_prefix}_BRANCH")

    if version:
        version = resolve_macros(version)
    if site:
        site = resolve_macros(site)
    if branch:
        branch = resolve_macros(branch)

    return {
        "file": mk_file,
        "version": version,
        "site": site,
        "branch": branch
    }


def is_git_hash(version_str):
    if not version_str:
        return False
    return len(version_str) == 40 and all(c in '0123456789abcdefABCDEF' for c in version_str)


# --- ROUTING LOGIC (The site router) ---

def get_pkg_versions(pkg, props):
    if not props or not props["version"]:
        return "", ""

    cur_version_raw = props["version"]
    site = props["site"] or ""
    branch = props["branch"] or ""

    # Legacy blacklists
    no_site_patterns = [
        "-legacy", "openbor6", "openbor7142", "qtsixa", "gpicase", "aml-dtbtools",
        "img-gpu-powervr", "noto-cjk-fonts", "uboot-powkiddy-a13", "uboot-visionfive2"
    ]
    is_no_site = any(pat in pkg or pat in props["file"] for pat in no_site_patterns)

    if is_no_site or not site:
        return cur_version_raw, ""

    # A raw, unresolved buildroot macro (e.g. leftover "$(SOME_VAR)" that
    # couldn't be resolved) means SITE isn't usable - bail out. But
    # "$(call github,...)" / "$(call gitlab,...)" are valid SITE forms that
    # the routing logic below explicitly understands (see "call github" /
    # "call gitlab" branches), so don't reject those just because they also
    # start with "$".
    if site.startswith('$') and not re.match(r'^\$\(call\s+(github|gitlab)\b', site):
        return cur_version_raw, ""

    if _DEBUG:
        print(f"[DEBUG] {pkg}: site={site!r} branch={branch!r} version={cur_version_raw!r}",
              file=sys.stderr)

    is_hash = is_git_hash(cur_version_raw)
    net_version = ""
    cur_version_display = cur_version_raw

    # Normalize/redirect legacy sites (e.g. rtkit upstream mirror to freedesktop gitlab)
    if "0pointer.net" in site or "git.0pointer.net" in site:
        site = "https://gitlab.freedesktop.org/pipewire/rtkit"

    def combine_ver_date(ver, dt):
        if ver and dt:
            return f"{ver} - {dt}"
        return ver or ""

    # Route matching
    if "call github" in site:
        m = re.search(r'call github,([^,]+),([^,]+)', site)
        if m:
            repo = f"{m.group(1).strip()}/{m.group(2).strip()}"
            if is_hash:
                sha, date = github_latest_commit(repo, branch or None)
                net_version = combine_ver_date(sha, date)
                cur_date = github_commit_info(repo, cur_version_raw)
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)
            else:
                tag, date = github_latest_tag_filtered(repo, r'proton-wine-[0-9]') if pkg.startswith("wine-proton") else github_latest_tag(repo)
                net_version = combine_ver_date(tag, date)
                cur_date = github_tag_info(repo, cur_version_raw) or github_tag_info(repo, f"v{cur_version_raw}")
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "call gitlab" in site:
        m = re.search(r'call gitlab,([^,]+),([^,]+)', site)
        if m:
            repo = f"{m.group(1).strip()}/{m.group(2).strip()}"
            if is_hash:
                sha, date = gitlab_latest_commit(repo, branch or None)
                net_version = combine_ver_date(sha, date)
                cur_date = gitlab_commit_info(repo, cur_version_raw)
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)
            else:
                tag, date = gitlab_latest_tag(repo)
                net_version = combine_ver_date(tag, date)
                cur_date = gitlab_tag_info(repo, cur_version_raw)
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "github.com" in site:
        m = re.search(r'github\.com/([^/]+/[^/]+)', site)
        if m:
            repo = m.group(1).replace(".git", "").strip()
            if is_hash:
                sha, date = github_latest_commit(repo, branch or None)
                net_version = combine_ver_date(sha, date)
                cur_date = github_commit_info(repo, cur_version_raw)
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)
            else:
                tag, date = github_latest_tag_filtered(repo, r'proton-wine-[0-9]') if pkg.startswith("wine-proton") else github_latest_tag(repo)
                net_version = combine_ver_date(tag, date)
                cur_date = github_tag_info(repo, cur_version_raw) or github_tag_info(repo, f"v{cur_version_raw}")
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "gitlab.com" in site:
        m = re.search(r'gitlab\.com/(.*)', site)
        if m:
            repo = m.group(1).replace(".git", "").strip()
            if is_hash:
                sha, date = gitlab_latest_commit(repo, branch or None)
                net_version = combine_ver_date(sha, date)
                cur_date = gitlab_commit_info(repo, cur_version_raw)
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)
            else:
                tag, date = gitlab_latest_tag(repo)
                net_version = combine_ver_date(tag, date)
                cur_date = gitlab_tag_info(repo, cur_version_raw)
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "bitbucket.org" in site:
        m = re.search(r'bitbucket\.org/([^/]+/[^/]+)', site)
        if m:
            repo = m.group(1).replace(".git", "").strip()
            if is_hash:
                html = fetch_url(f"https://bitbucket.org/{repo}/commits/branch/{branch or 'master'}")
                if html:
                    m_c = re.search(r'/commits/([0-9a-f]{40})', html)
                    net_version = m_c.group(1) if m_c else ""
            else:
                html = fetch_url(f"https://bitbucket.org/{repo}/downloads/?tab=tags")
                if html:
                    m_t = re.findall(r'"name">([^<]+)', html)
                    filtered = [t for t in m_t if t != "Tag"]
                    net_version = filtered[0] if filtered else ""

    elif "richwhitehouse.com" in site:
        net_version = richwhitehouse_latest()
    elif "redream" in site or "redream." in site:
        net_version = redream_latest()
    elif "sourceforge.net" in site:
        net_version = sourceforge_latest()
    elif "abuse.zoy.org" in site:
        net_version = abusedata_latest()

    elif "voidpoint.io" in site:
        m = re.search(r'voidpoint\.io/([^/]+/[^/]+)', site)
        if m:
            repo = m.group(1).strip()
            sha, date = voidpoint_latest_commit(repo, branch or None)
            net_version = combine_ver_date(sha, date)
            html_c = fetch_url(f"https://voidpoint.io/{repo}/-/commit/{cur_version_raw}")
            cur_date = ""
            if html_c:
                m_d = re.search(r'data-container="body">([^<]+)</time>', html_c)
                if m_d:
                    cur_date = m_d.group(1)
            cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "winehq.org/git" in site:
        m = re.search(r'winehq\.org/git/(.*)', site)
        if m:
            repo = m.group(1).strip()
            if not repo.endswith(".git"):
                repo += ".git"
            if is_hash:
                sha, date = winehqgit_latest_commit(repo)
                net_version = combine_ver_date(sha, date)
                html_c = fetch_url(f"https://source.winehq.org/git/{repo}/commit/{cur_version_raw}")
                cur_date = ""
                if html_c:
                    m_d = re.search(r'datetime">([^<]+)', html_c)
                    if m_d:
                        date_str = m_d.group(1)
                        m_date = re.match(r'.*?,\s*(\S+)\s+(\S+)\s+(\S+)', date_str)
                        if m_date:
                            cur_date = f"{m_date.group(2)} {m_date.group(1)}, {m_date.group(3)}"
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)
            else:
                tag, date = winehqgit_latest_tag(repo)
                net_version = combine_ver_date(tag, date)
                html_tags = fetch_url(f"https://source.winehq.org/git/{repo}/tags")
                cur_date = ""
                if html_tags:
                    for line in html_tags.splitlines():
                        if cur_version_raw in line:
                            m_c = re.search(r'/commit/([0-9a-f]{40})', line)
                            if m_c:
                                sha = m_c.group(1)
                                html_c = fetch_url(f"https://source.winehq.org/git/{repo}/commit/{sha}")
                                if html_c:
                                    m_d = re.search(r'datetime">([^<]+)', html_c)
                                    if m_d:
                                        date_str = m_d.group(1)
                                        m_date = re.match(r'.*?,\s*(\S+)\s+(\S+)\s+(\S+)', date_str)
                                        if m_date:
                                            cur_date = f"{m_date.group(2)} {m_date.group(1)}, {m_date.group(3)}"
                                break
                cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "dl.winehq.org" in site:
        m = re.search(r'\.org/(.*)', site)
        if m:
            path = m.group(1).rstrip("/")
            tag, date = winehqdl_latest(path)
            net_version = combine_ver_date(tag, date)
            html_p = fetch_url(f"https://dl.winehq.org/{path}/")
            cur_date = ""
            if html_p:
                for line in html_p.splitlines():
                    if cur_version_raw in line:
                        m_d = re.search(r'mod">([^<]+?)\s+\d+:\d+', line)
                        if m_d:
                            cur_date = m_d.group(1).strip()
                            break
            cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "sindenlightgun" in site:
        net_version = sinden_lightgun_latest()
    elif "mirrors.kodi.tv" in site:
        net_version = kodi_resources_latest(site)
    elif "ftp.denx.de" in site:
        net_version = uboot_multiboard_latest(site)
    elif "busybox.net" in site:
        net_version = initramfs_latest(site)
    elif "ftp.debian.org" in site:
        net_version = shim_signed_efi_ia32_latest(site)
    elif "launchpad.net/ubuntu" in site:
        net_version = shim_signed_efi_x64_latest()

    elif "git.tuxfamily.org" in site:
        tag, date = hatari_latest(site)
        net_version = combine_ver_date(tag, date)
        html_t = fetch_url(f"{site}/tag/?id=v{cur_version_raw}")
        cur_date = ""
        if html_t:
            m_d = re.search(r'tag date</td><td>([^<]+?)\s+\d+:\d+', html_t)
            if m_d:
                cur_date = m_d.group(1).strip()
        cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "git.kernel.org" in site:
        base_url = site.split("/snapshot")[0]
        net_version = all_linux_firmware_latest(base_url)
    elif "archive.mesa3d.org" in site:
        net_version = mesa3d_latest()
    elif "download.nvidia.com" in site:
        net_version = nvidia_latest()
    elif "pythonhosted.org" in site or "pypi.python.org" in site:
        net_version = python_hosted_latest(pkg)
    elif "kryoflux.com" in site:
        net_version = kyroflux_latest(pkg)
    elif "enet.bespin.org" in site:
        net_version = libenet_latest()
    elif "ijg.org" in site:
        net_version = jpegsrc_latest()
    elif "openmpt.org" in site:
        net_version = libopenmpt_latest()
    elif "/p/sc2/uqm" in site:
        net_version = uqm_latest()
    elif "linaro.org" in site:
        net_version = linaro_latest()
    elif "cabextract.org.uk" in site:
        net_version = cabextract_latest()
    elif "/pacman" in site:
        net_version = pacman_latest()
    elif "pm-utils.freedesktop.org" in site:
        net_version = pmutils_latest()

    elif "gitlab.freedesktop.org" in site:
        m = re.search(r'\.org/([^/]+/[^/]+)', site)
        if m:
            repo = m.group(1).strip()
            if _DEBUG:
                print(f"[DEBUG] {pkg}: gitlab.freedesktop.org repo={repo!r}", file=sys.stderr)
            tag, date = gitlab_freedesktop_latest_tag(repo)
            if _DEBUG:
                print(f"[DEBUG] {pkg}: gitlab_freedesktop_latest_tag -> tag={tag!r} date={date!r}",
                      file=sys.stderr)
            net_version = combine_ver_date(tag, date)
            tag_query = f"v{cur_version_raw}" if pkg == "libliftoff" else cur_version_raw
            html_t = fetch_url(f"https://gitlab.freedesktop.org/{repo}/-/tags/{tag_query}")
            cur_date = ""
            if html_t:
                m_d = re.search(r'data-container="body">([^<]+)</time>', html_t)
                if m_d:
                    cur_date = m_d.group(1)
            cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    elif "floodgap.com" in site:
        net_version = floodgap_xa_latest()
    elif "adwaita-icon-theme" in site:
        net_version = adwaita_icon_theme_latest()

    elif "git.sr.ht" in site:
        m = re.search(r'\.ht/([^/]+/[^/]+)', site)
        if m:
            repo = m.group(1).strip()
            tag, date = sourcehut_latest_tag(repo)
            net_version = combine_ver_date(tag, date)
            html_t = fetch_url(f"https://git.sr.ht/{repo}/refs/v{cur_version_raw}")
            cur_date = ""
            if html_t:
                m_d = re.search(r'datetime="([^"]+?)"[^>]*>.*?UTC', html_t)
                if m_d:
                    cur_date = m_d.group(1)
            cur_version_display = combine_ver_date(cur_version_raw, cur_date)

    normalized_cur = cur_version_display
    if normalized_cur.startswith("v"):
        normalized_cur = normalized_cur[1:]
    if net_version.startswith("v") and not normalized_cur.startswith("v"):
        net_version = net_version[1:]

    return cur_version_display, net_version


# --- CORE OPERATIONAL LOGIC ---

def get_all_packages():
    search_path = os.path.join("package", "batocera")
    if not os.path.isdir(search_path):
        search_path = "./package"

    all_pkgs = []
    if os.path.isdir(search_path):
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith(".mk") and file != "batocera.mk":
                    all_pkgs.append(file[:-3])
    return sorted(list(set(all_pkgs)))


def resolve_packages(args):
    resolved = []
    for arg in args:
        if arg == "ALL":
            return get_all_packages()
        elif arg == "ALLGROUPS":
            for g in GROUPS:
                resolved.extend(GROUPS[g])
        elif arg in GROUPS:
            resolved.extend(GROUPS[arg])
        else:
            resolved.append(arg)

    seen = set()
    deduped = []
    for r in resolved:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    return deduped


def show_help():
    print(f"Syntax: {sys.argv[0]} [package | PACKAGEGROUP]...")
    print(f"    or: {sys.argv[0]} --update [package | PACKAGEGROUP]...")
    print("")
    print("[package] can be any of the *.mk under ./package/batocera/ (without \".mk\")")
    print(f"Example: {sys.argv[0]} libretro-mame libretro-fbneo")
    print("")
    print("[PACKAGEGROUP] can be RETROARCH, LIBRETRO, MUPEN, OPENBOR, EMULATORS, PORTS, WINE, CONTROLLERS, UTILS, ALLGROUPS, ALL")
    sys.exit(1)


def _version_only(s):
    """Strip the trailing ' - <date>' suffix and any leading 'v' so that
    version comparisons aren't thrown off by a date that failed to resolve
    for one side but not the other."""
    if not s:
        return ""
    return s.split(" - ")[0].strip().lstrip("vV")


def run_check(packages):
    results = []

    def check_one(pkg):
        props = parse_mk_properties(pkg)
        if not props:
            return pkg, "not found (run from top buildroot dir)", ""
        cur, net = get_pkg_versions(pkg, props)
        return pkg, cur, net

    print(f"\nSelection size: {len(packages)} packages")
    print("+" + "-"*42 + "+" + "-"*62 + "+" + "-"*62 + "+")
    print(f"| {'Package':<40} | {'Available version':<60} | {'Version':<60} |")
    print("+" + "-"*42 + "+" + "-"*62 + "+" + "-"*62 + "+")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_pkg = {executor.submit(check_one, pkg): pkg for pkg in packages}
        for future in as_completed(future_to_pkg):
            pkg, cur, net = future.result()
            results.append((pkg, cur, net))

    results.sort(key=lambda x: x[0])

    CYAN = "\033[1;36m"

    for pkg, cur, net in results:
        cur_v = _version_only(cur)
        net_v = _version_only(net)

        if net.startswith("BLOCKED-BY-ANTIBOT"):
            msg = "(blocked by anti-bot challenge - check manually)"
            print(f"| {pkg:<40} | {CYAN}{msg:<60}{RESET} | {cur:<60} |")
        elif cur.startswith("master"):
            print(f"| {pkg:<40} | {net:<60} | {YELLOW}{cur:<60}{RESET} |")
        elif net_v and net_v == cur_v:
            print(f"| {pkg:<40} | {'':<60} | {GREEN}{cur:<60}{RESET} |")
        elif not net:
            print(f"| {pkg:<40} | {net:<60} | {PINK}{cur:<60}{RESET} |")
        else:
            print(f"| {pkg:<40} | {net:<60} | {RED}{cur:<60}{RESET} |")

    print("+" + "-"*42 + "+" + "-"*62 + "+" + "-"*62 + "+")


def base_update(pkg, new_ver):
    props = parse_mk_properties(pkg)
    if not props or not props["file"]:
        return False

    filepath = props["file"]
    var_prefix = pkg.replace("-", "_").upper()

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    updated = False
    pattern = re.compile(rf"^(\s*{var_prefix}_VERSION\s*=\s*)(.*?)\s*$")
    for line in lines:
        if line.strip().startswith("#"):
            new_lines.append(line)
            continue

        m = pattern.match(line)
        if m:
            new_lines.append(f"{m.group(1)}{new_ver}\n")
            updated = True
        else:
            new_lines.append(line)

    if updated:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    return False


def run_update(packages):
    for pkg in packages:
        props = parse_mk_properties(pkg)
        if not props:
            print(f"Package {pkg} not found!")
            continue

        cur, net = get_pkg_versions(pkg, props)
        cur_str = cur.split()[0] if cur else ""
        net_str = net.split()[0] if net else ""

        print(f"Checking {pkg}...")
        print(f"  Current version: {cur_str}")

        if net_str:
            if net_str.startswith("v") and not cur_str.startswith("v"):
                net_str = net_str[1:]

            if net_str != cur_str:
                print(f"  New version found: {net_str}")
                if base_update(pkg, net_str):
                    print("  Updated successfully.")
                else:
                    print("  Failed to update variable in file.")
            else:
                print("  Package already up to date.")
            print(f"| {pkg:<40} | {GREEN}{net:<60}{RESET} |\n")
        else:
            print("  No update found.")
            print(f"| {pkg:<40} | {RED}{cur:<60}{RESET} |\n")


# --- ENTRY POINT ---
if __name__ == "__main__":
    if not os.path.isdir("./package/batocera") and not os.path.isdir("./package"):
        print("ERROR: This script must be run from the git root directory of the buildroot project.")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        show_help()

    if args[0] == "--update":
        if len(args) < 2:
            show_help()
        pkgs = resolve_packages(args[1:])
        run_update(pkgs)
    elif args[0].startswith("-"):
        show_help()
    else:
        pkgs = resolve_packages(args)
        run_check(pkgs)
