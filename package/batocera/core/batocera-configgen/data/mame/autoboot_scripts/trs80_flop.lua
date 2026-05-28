-- trs80_flop.lua
-- Autoboot for CoCo floppy disks: compute SHA1 of the disk image,
-- look up the "basic" command in coco_sha1_map.json, and type it.

local SHA1_MAP_PATH = "/usr/share/batocera/configgen/data/mame/autoboot_scripts/coco_sha1_map.json"

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local frame_num   = 0
local boot_command = nil


-- ── Path helpers ──────────────────────────────────────────────────────────────

local function has_os9_name_hint(path)
    local lower = path:lower()
    return lower:find("%(os%-9%)", 1, false) ~= nil
end



-- ── SHA1 computation ──────────────────────────────────────────────────────────

local function sha1_of_file(filepath)
    local fq  = filepath:gsub("'", "'\\''")
    local pipe = io.popen(string.format("sha1sum '%s' 2>/dev/null", fq), "r")
    if not pipe then return nil end
    local line = pipe:read("*l")
    pipe:close()
    return line and line:match("^(%x+)")
end

local function sha1_of_bytes(data)
    local tmp = "/tmp/coco_sha1_tmp.bin"
    local f   = io.open(tmp, "wb")
    if not f then return nil end
    f:write(data)
    f:close()
    local pipe = io.popen("sha1sum '" .. tmp .. "' 2>/dev/null", "r")
    if not pipe then os.remove(tmp); return nil end
    local line = pipe:read("*l")
    pipe:close()
    os.remove(tmp)
    return line and line:match("^(%x+)")
end

local function compute_sha1(mame_filename)
    local kind, zippath, entrypath = zip_util.parse_mame_path(mame_filename)
    if kind == "zip" then
        print(string.format("[CoCo Flop] ZIP: '%s'  entry: '%s'", zippath, entrypath))
        local data = zip_util.read_entry_from_zip(zippath, entrypath, nil)
        if not data then return nil end
        return sha1_of_bytes(data)
    else
        return sha1_of_file(entrypath)
    end
end


-- ── JSON lookup ───────────────────────────────────────────────────────────────

-- Decode a JSON string value (handles \n \r \t \" \\ escapes).
local function decode_json_string(json_str, start_pos)
    local result = {}
    local i = start_pos  -- points to the char after the opening "
    while i <= #json_str do
        local c = json_str:sub(i, i)
        if c == "\\" then
            i = i + 1
            local e = json_str:sub(i, i)
            if     e == "n"  then table.insert(result, "\n")
            elseif e == "r"  then table.insert(result, "\r")
            elseif e == "t"  then table.insert(result, "\t")
            elseif e == '"'  then table.insert(result, '"')
            elseif e == "\\" then table.insert(result, "\\")
            else               table.insert(result, e)
            end
        elseif c == '"' then
            break  -- end of JSON string
        else
            table.insert(result, c)
        end
        i = i + 1
    end
    return table.concat(result)
end

-- Extract the value of a JSON key from a small JSON object string.
local function json_get_string(block, key)
    local search = '"' .. key:gsub("([%(%)%.%%%+%-%*%?%[%^%$])", "%%%1") .. '"'
    local kpos   = block:find(search, 1, true)
    if not kpos then return nil end
    -- skip past key, optional whitespace, colon, optional whitespace, opening quote
    local qpos = block:find('"', kpos + #search + 1)  -- +1 for the colon
    if not qpos then return nil end
    return decode_json_string(block, qpos + 1)
end

-- Load coco_sha1_map.json and return the "basic" field for the given sha1, or nil.
local function lookup_sha1(sha1)
    local f = io.open(SHA1_MAP_PATH, "r")
    if not f then
        print("[CoCo Flop] Cannot open SHA1 map: " .. SHA1_MAP_PATH)
        return nil
    end
    local content = f:read("*a")
    f:close()

    local key_start = content:find('"' .. sha1 .. '"', 1, true)
    if not key_start then
        print("[CoCo Flop] SHA1 not in map: " .. sha1)
        return nil
    end

    -- Extract the balanced {} block for this entry
    local brace_start = content:find("{", key_start)
    if not brace_start then return nil end
    local depth, i = 0, brace_start
    while i <= #content do
        local c = content:sub(i, i)
        if     c == "{" then depth = depth + 1
        elseif c == "}" then
            depth = depth - 1
            if depth == 0 then
                return json_get_string(content:sub(brace_start, i), "basic")
            end
        end
        i = i + 1
    end
    return nil
end


-- ── Floppy image discovery ────────────────────────────────────────────────────

local function find_dsk_in_zip(zippath)
    return zip_util.find_zip_entry(zippath, function(n) return n:lower():match("%.dsk$") end)
end

local function find_floppy_path()
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.dsk") or fn:find("%.dmk") or fn:find("%.vdk") then
                print("[CoCo Flop] Floppy image: " .. img.filename)
                return img.filename
            end
            -- Bare .zip: resolve the DSK entry name and return a virtual path
            if fn:match("%.zip$") then
                local dsk = find_dsk_in_zip(img.filename)
                if dsk then
                    local vpath = img.filename .. "/" .. dsk
                    print("[CoCo Flop] Floppy image (zip): " .. vpath)
                    return vpath
                end
            end
        end
    end
    return nil
end


-- ── RSDOS directory parser ────────────────────────────────────────────────────
-- Standard CoCo JVC disk: 35 tracks, 18 sectors/track, 256 bytes/sector.
-- Directory starts at track 17 (0-based), sector index 2 (sector 3, 1-based).
-- Each 32-byte entry: bytes 0-7 name, 8-10 extension, 11 file type
--   type 0=BASIC tokenized  type 1=data  type 2=machine code  type 3=ASCII BASIC

local RSDOS_DIR_OFFSET = (17 * 18 + 2) * 256   -- 78848

-- Detect OS-9 disk via LSN0 (track 0, sector 1, offset 0) field values.
-- OS-9 stores DD.TKS (sectors/track) at byte 3; CoCo standard = 0x12 (18).
-- DD.TOT (total sectors, 3 bytes big-endian) at bytes 0-2 is > 0 and byte 0 = 0x00.
-- RSDOS disks have 0xFF at byte 0 (blank sector) so this is unambiguous.
-- A dual-format disk may have both OS-9 LSN0 and a valid RSDOS directory;
-- RSDOS is preferred in that case (BASIC boots first on a dual-format disk).
local function is_os9_disk(disk_data)
    if #disk_data < 4 then return false end
    local b0  = disk_data:byte(1)  -- DD.TOT high byte (0x00 for any sane floppy)
    local tks = disk_data:byte(4)  -- DD.TKS = sectors per track
    return b0 == 0x00 and tks == 0x12
end

local function parse_rsdos_dir_data(data)
    local all_ff    = true   -- every slot is 0xFF (no directory at all)
    local first_cmd = nil    -- first runnable entry found
    local boot_cmd  = nil    -- entry named BOOT (takes priority)

    for idx = 0, 71 do
        local off = idx * 32 + 1  -- 1-based Lua index
        if off + 31 > #data then break end

        local first = data:byte(off)
        if first == 0x00 then
            all_ff = false

            -- Some real-world images contain 0x00-prefixed garbage/deleted slots
            -- before later valid entries. Only treat an all-zero slot as true
            -- end-of-directory; otherwise skip and keep scanning.
            local all_zero = true
            for i = 1, 31 do
                if data:byte(off + i) ~= 0x00 then
                    all_zero = false
                    break
                end
            end
            if all_zero then
                break
            end

            print(string.format("[CoCo Flop] Dir[%d]: skipping 0x00-prefixed slot", idx))
            goto continue
        end

        if first ~= 0xFF then
            all_ff = false

            -- Non-ASCII first byte: garbled entry (OS-9 data, copy-protection, etc.) — skip it.
            if first > 0x7E or first < 0x20 then
                print(string.format("[CoCo Flop] Dir[%d]: skipping garbled entry (first=0x%02x)", idx, first))
                goto continue
            end

            -- Collect all 8 name bytes up to NUL, then rtrim spaces.
            -- Mid-name spaces are valid (e.g. "3D GHOST"); only trailing padding stripped.
            local name = {}
            local garbled = false
            for i = 0, 7 do
                local c = data:byte(off + i)
                if c == 0x00 then break end
                if c > 0x7E then garbled = true; break end
                table.insert(name, string.char(c))
            end
            if garbled then
                print(string.format("[CoCo Flop] Dir[%d]: skipping garbled name", idx))
                goto continue
            end
            local name_str = table.concat(name):match("^(.-)%s*$")

            local ext = {}
            local ext_garbled = false
            for i = 8, 10 do
                local c = data:byte(off + i)
                if c == 0x00 then break end
                -- Extension must be alphanumeric or space; anything else is OS-9 data
                if not ((c >= 0x30 and c <= 0x39) or (c >= 0x41 and c <= 0x5A)
                        or (c >= 0x61 and c <= 0x7A) or c == 0x20) then
                    ext_garbled = true; break
                end
                table.insert(ext, string.char(c))
            end
            if ext_garbled then
                print(string.format("[CoCo Flop] Dir[%d]: skipping garbled extension", idx))
                goto continue
            end
            local ext_str = table.concat(ext):match("^(.-)%s*$")

            local file_type = data:byte(off + 11)

            -- Valid RSDOS file types: 0=BASIC tokenized, 1=data, 2=machine code, 3=ASCII BASIC.
            -- Any other value means this is not a real RSDOS directory entry.
            if file_type > 3 then
                print(string.format("[CoCo Flop] Dir[%d]: skipping invalid ftype=%d", idx, file_type))
                goto continue
            end

            if #name_str > 0 and file_type ~= 1 then
                -- Infocom Z-machine disks store the interpreter as GAME.BIN but boot via DOS
                if name_str == "GAME" and ext_str == "BIN" and file_type == 2 then
                    print("[CoCo Flop] GAME.BIN detected → DOS")
                    return "DOS\n"
                end

                local cmd
                if file_type == 0 or file_type == 3 or ext_str == "BAS" then
                    cmd = 'RUN "' .. name_str .. '"\n'
                else
                    cmd = 'LOADM "' .. name_str .. '":EXEC\n'
                end

                print(string.format(
                    "[CoCo Flop] Dir[%d]: '%s.%s' type=%d  cmd=%s",
                    idx, name_str, ext_str, file_type, cmd:gsub("\n", "\\n")))

                if name_str == "BOOT" then
                    boot_cmd = cmd
                elseif first_cmd == nil then
                    first_cmd = cmd
                end
            end
        end
        ::continue::
    end

    -- All 72 slots were 0xFF: no RSDOS directory — likely a bootable disk (e.g. Infocom Z-machine)
    if all_ff then
        print("[CoCo Flop] All-0xFF directory: bootable disk → DOS")
        return "DOS\n"
    end

    local cmd = boot_cmd or first_cmd
    if cmd then
        if boot_cmd then
            print("[CoCo Flop] Using BOOT entry: " .. cmd:gsub("\n", "\\n"))
        end
        return cmd
    end

    print("[CoCo Flop] No runnable program found in disk directory.")
    return nil
end

local function read_disk_dir_command(mame_filename)
    local kind, zippath, entrypath = zip_util.parse_mame_path(mame_filename)
    local disk_data, dir_data

    if (kind == "zip" and zippath and has_os9_name_hint(zippath)) or has_os9_name_hint(entrypath) then
        print("[CoCo Flop] OS-9 filename hint detected → DOS")
        return "DOS\n"
    end

    if kind == "zip" then
        disk_data = zip_util.read_entry_from_zip(zippath, entrypath, nil)
        if disk_data and #disk_data > RSDOS_DIR_OFFSET then
            dir_data = disk_data:sub(RSDOS_DIR_OFFSET + 1, RSDOS_DIR_OFFSET + 72 * 32)
        end
    else
        local f = io.open(entrypath, "rb")
        if not f then
            print("[CoCo Flop] Cannot open disk: " .. entrypath)
            return nil
        end
        disk_data = f:read("*a")
        f:close()
        if disk_data and #disk_data > RSDOS_DIR_OFFSET then
            dir_data = disk_data:sub(RSDOS_DIR_OFFSET + 1, RSDOS_DIR_OFFSET + 72 * 32)
        end
    end

    if not dir_data or #dir_data == 0 then
        print("[CoCo Flop] Could not read directory sector from disk.")
        return nil
    end

    local cmd = parse_rsdos_dir_data(dir_data)
    if cmd then return cmd end

    -- No valid RSDOS directory found — check OS-9 sector at LSN0
    if disk_data and is_os9_disk(disk_data) then
        print("[CoCo Flop] OS-9 disk signature detected → DOS")
        return "DOS\n"
    end

    return nil
end


-- ── Boot command detection ────────────────────────────────────────────────────

local function detect_boot_command()
    print("[CoCo Flop] --- Boot detection ---")

    local path = find_floppy_path()
    if not path then
        print("[CoCo Flop] No floppy image found.")
        return nil
    end
    print("[CoCo Flop] Path: " .. path)

    local sha1 = compute_sha1(path)
    if sha1 then
        print("[CoCo Flop] SHA1: " .. sha1)
        local cmd = lookup_sha1(sha1)
        if cmd then
            print("[CoCo Flop] SHA1 match: " .. cmd:gsub("\n", "\\n"):gsub("\r", "\\r"))
            return cmd
        end
        print("[CoCo Flop] Not in SHA1 map — parsing disk directory.")
    else
        print("[CoCo Flop] Could not compute SHA1 — parsing disk directory.")
    end

    return read_disk_dir_command(path)
end


-- ── Main frame callback ───────────────────────────────────────────────────────

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        boot_command = detect_boot_command()
        if boot_command then
            emu.print_info("[CoCo Flop] Autoboot: " .. boot_command:gsub("\n", "\\n"))
        else
            emu.print_info("[CoCo Flop] No autoboot.")
        end
    end

    if frame_num % 100 == 0 then
        emu.print_info("Current Frame: " .. frame_num)
    end

    if boot_command then
        common_autoboot.type_at_frame(frame_num, boot_command, 150)
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
