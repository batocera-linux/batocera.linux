-- atom_flop.lua
-- Autoboot Acorn Atom floppy disks by inspecting the Atom DOS directory.

local zip_util = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local DISK_SCAN_BYTES = 512
local DIR_ENTRY_SIZE = 8
local DIR_ENTRY_COUNT = 32
local TYPE_DELAY = 120

print("[Atom Flop] Loaded from: " .. debug.getinfo(1, 'S').source)

local frame_num = 0
local boot_program = nil
local boot_started = false
local boot_stage = 0
local next_stage_frame = 0
local f14_key_down = false
local digit_key_down = nil
local lowercase_started = false
local lowercase_text = nil
local lowercase_index = 1
local lowercase_key = nil
local lowercase_done_frame = 0
local lowercase_next_frame = 0
local lowercase_release_frame = 0
local lowercase_close_posted = false

local DOS_SETTLE_FRAMES = 140
local F14_PREFIX_DELAY = 40
local F14_DIGIT_DELAY = 90
local F14_SUFFIX_DELAY = 130
local F14_KEY_HOLD_FRAMES = 20
local JSW2_PREFIX_DELAY = 40
local JSW2_DIGIT_DELAY = 500
local JSW2_SUFFIX_DELAY = 130
local DIGIT_KEY_HOLD_FRAMES = 200
local LOWERCASE_START_DELAY = 90
local LOWERCASE_KEY_HOLD_FRAMES = 16
local LOWERCASE_KEY_GAP_FRAMES = 12

local LETTER_KEYS = {
    A = { "Y6", 0x08 },
    B = { "Y5", 0x08 },
    C = { "Y4", 0x08 },
    D = { "Y3", 0x08 },
    E = { "Y2", 0x08 },
    F = { "Y1", 0x08 },
    G = { "Y0", 0x08 },
    H = { "Y9", 0x10 },
    I = { "Y8", 0x10 },
    J = { "Y7", 0x10 },
    K = { "Y6", 0x10 },
    L = { "Y5", 0x10 },
    M = { "Y4", 0x10 },
    N = { "Y3", 0x10 },
    O = { "Y2", 0x10 },
    P = { "Y1", 0x10 },
    Q = { "Y0", 0x10 },
    R = { "Y9", 0x20 },
    S = { "Y8", 0x20 },
    T = { "Y7", 0x20 },
    U = { "Y6", 0x20 },
    V = { "Y5", 0x20 },
    W = { "Y4", 0x20 },
    X = { "Y3", 0x20 },
    Y = { "Y2", 0x20 },
    Z = { "Y1", 0x20 },
}

local DIGIT_KEYS = {
    ["1"] = { "Y2", 0x02 },
    ["2"] = { "Y1", 0x02 },
    ["3"] = { "Y0", 0x02 },
    ["4"] = { "Y9", 0x04 },
    ["5"] = { "Y8", 0x04 },
    ["6"] = { "Y7", 0x04 },
    ["7"] = { "Y6", 0x04 },
    ["8"] = { "Y5", 0x04 },
    ["9"] = { "Y4", 0x04 },
    ["0"] = { "Y3", 0x02 },
}

local PREFERRED_PROGRAMS = {
    -- Prefer colour variants when both colour and mono are present.
    "CCHUCK",
    "CGALA",

    "LOADER",
    "JOE",
    "EHRUN",
    "F14RUN",
    "GALAXI",
    "JSW2RUN",
    "JSWRUN",
    "JUNGLE",
    "MMRUN",
    "RUNME",
    "REPLOAD",
}

local function find_disk_in_zip(zippath)
    return zip_util.find_zip_entry(zippath, function(n)
        return n:lower():match("%.dsk$") or n:lower():match("%.40t$")
    end)
end

local function is_atom_floppy_name(path)
    local lower = path:lower()
    return lower:match("%.dsk$") or lower:match("%.40t$") or lower:match("%.mfi$") or
           lower:match("%.dfi$") or lower:match("%.hfe$") or lower:match("%.mfm$") or
           lower:match("%.td0$") or lower:match("%.imd$") or lower:match("%.d77$") or
           lower:match("%.d88$") or lower:match("%.1dd$") or lower:match("%.cqm$") or
           lower:match("%.cqi$")
end

local function find_floppy_path()
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename
            local lower = fn:lower()
            if is_atom_floppy_name(lower) or lower:find("%.zip/") then
                print("[Atom Flop] Floppy image: " .. fn)
                return fn
            end
            if lower:match("%.zip$") then
                local entry = find_disk_in_zip(fn)
                if entry then
                    local vpath = fn .. "/" .. entry
                    print("[Atom Flop] Floppy image (zip): " .. vpath)
                    return vpath
                end
            end
        end
    end
    return nil
end

local function clean_dir_name(raw)
    local chars = {}
    for i = 1, #raw do
        local c = raw:byte(i)
        if c == 0x00 then break end
        if c < 0x20 or c > 0x7e then return nil end
        table.insert(chars, string.char(c))
    end

    local name = table.concat(chars):match("^%s*(.-)%s*$")
    if name == "" then return nil end
    return name
end

local function parse_atom_dir(data)
    local names = {}
    local present = {}
    if not data or #data < DIR_ENTRY_SIZE then return names, present end

    for idx = 0, DIR_ENTRY_COUNT - 1 do
        local off = idx * DIR_ENTRY_SIZE + 1
        if off + DIR_ENTRY_SIZE - 1 > #data then break end
        local raw = data:sub(off, off + DIR_ENTRY_SIZE - 1)
        local name = clean_dir_name(raw)
        if name then
            table.insert(names, name)
            present[name:upper()] = name
            print(string.format("[Atom Flop] Dir[%d]: %s", idx, name))
        end
    end

    return names, present
end

local function choose_from_directory(names, present)
    for _, wanted in ipairs(PREFERRED_PROGRAMS) do
        if present[wanted] then return present[wanted] end
    end

    for _, name in ipairs(names) do
        local upper = name:upper()
        if upper:match("RUN$") and not upper:match("SCRRUN$") then
            return name
        end
    end

    if present["RUNME"] then return present["RUNME"] end
    return nil
end

local function normalize_boot_program(program)
    if program and program:upper() == "REPLOADED" then
        return "REPLOAD"
    end
    return program
end

local function detect_boot_program()
    print("[Atom Flop] --- Floppy autoboot detection ---")

    local path = find_floppy_path()
    if not path then
        print("[Atom Flop] No floppy image found.")
        return nil
    end

    local data = zip_util.read_bytes(path, DISK_SCAN_BYTES)
    if data then
        local names, present = parse_atom_dir(data)
        local from_dir = choose_from_directory(names, present)
        if from_dir then
            print("[Atom Flop] Selected from directory: " .. from_dir)
            return normalize_boot_program(from_dir)
        end
    end

    print("[Atom Flop] No runnable program detected.")
    return nil
end

local function key_1_field()
    local port = manager.machine.ioport.ports[":Y2"]
    return port and port:field(0x02) or nil
end

local function digit_field(digit)
    local keydef = DIGIT_KEYS[digit]
    if not keydef then return nil end
    local port = manager.machine.ioport.ports[":" .. keydef[1]]
    return port and port:field(keydef[2]) or nil
end

local function shift_field()
    local port = manager.machine.ioport.ports[":Y10"]
    return port and port:field(0x80) or nil
end

local function letter_field(letter)
    local keydef = LETTER_KEYS[letter:upper()]
    if not keydef then return nil end
    local port = manager.machine.ioport.ports[":" .. keydef[1]]
    return port and port:field(keydef[2]) or nil
end

local function set_digit_key(digit, pressed)
    local field = digit_field(digit)
    if not field then
        print("[Atom Flop] Missing key field for digit " .. digit .. ", falling back to keypost")
        if pressed then
            emu.keypost(digit)
        end
        return
    end
    if pressed then
        field:set_value(1)
        digit_key_down = digit
    else
        field:clear_value()
        digit_key_down = nil
    end
end

local function set_key_1(pressed)
    local field = key_1_field()
    if not field then
        print("[Atom Flop] Missing key field for 1")
        return
    end
    if pressed then
        field:set_value(1)
        f14_key_down = true
    else
        field:clear_value()
        f14_key_down = false
    end
end

local function has_lowercase(text)
    return text:find("%l") ~= nil
end

local function start_lowercase_text(text, target_frame)
    if frame_num == target_frame and not lowercase_started then
        print("[Atom Flop] Typing lowercase via matrix: " .. text)
        lowercase_text = text
        lowercase_index = 1
        lowercase_next_frame = frame_num
        lowercase_started = true
    end
end

local function release_lowercase_key()
    if lowercase_key then
        local field = letter_field(lowercase_key)
        if field then field:clear_value() end
        lowercase_key = nil
    end
    local shift = shift_field()
    if shift then shift:clear_value() end
    lowercase_next_frame = frame_num + LOWERCASE_KEY_GAP_FRAMES
end

local function process_lowercase_text()
    if not lowercase_started or lowercase_done_frame ~= 0 then return end

    if lowercase_key and frame_num >= lowercase_release_frame then
        release_lowercase_key()
        lowercase_index = lowercase_index + 1
        if lowercase_index > #lowercase_text then
            lowercase_done_frame = lowercase_next_frame
        end
        return
    end

    if lowercase_key or frame_num < lowercase_next_frame then return end

    local ch = lowercase_text:sub(lowercase_index, lowercase_index)
    local field = letter_field(ch)
    local shift = shift_field()
    if not field or not shift then
        print("[Atom Flop] Missing lowercase key field for: " .. ch)
        lowercase_done_frame = frame_num
        return
    end

    shift:set_value(1)
    field:set_value(1)
    lowercase_key = ch
    lowercase_release_frame = frame_num + LOWERCASE_KEY_HOLD_FRAMES
end

local function keypost_at(text, target_frame)
    if frame_num == target_frame then
        print("[Atom Flop] Typing: " .. text:gsub("\n", "\\n"))
        emu.keypost(text)
    end
end

local function process_frame()
    frame_num = frame_num + 1

    if not boot_program then
        boot_program = detect_boot_program()
        if not boot_program then
            subscription:unsubscribe()
            return
        end
    end

    if not boot_started then
        boot_started = true
        print("[Atom Flop] Booting with *RUN\"" .. boot_program .. "\"")
    end

    keypost_at("*DOS\n", TYPE_DELAY)

    if boot_stage == 0 and frame_num == TYPE_DELAY then
        print("[Atom Flop] Queueing: *DOS")
        next_stage_frame = frame_num + DOS_SETTLE_FRAMES
        boot_stage = 1
    elseif boot_stage == 1 and frame_num >= next_stage_frame then
        print("[Atom Flop] Entering stage 3 at frame " .. frame_num .. ", next_stage_frame=" .. next_stage_frame)
        print("[Atom Flop] Typing run command for: " .. boot_program)
        boot_stage = 3
    end

    if boot_stage == 3 and boot_program:upper() == "F14RUN" then
        keypost_at("*RUN\"F", next_stage_frame + F14_PREFIX_DELAY)
        if frame_num == next_stage_frame + F14_DIGIT_DELAY then
            print("[Atom Flop] Pressing Atom key 1")
            set_key_1(true)
        elseif f14_key_down and frame_num == next_stage_frame + F14_DIGIT_DELAY + F14_KEY_HOLD_FRAMES then
            set_key_1(false)
        end
        keypost_at("4RUN\"\n", next_stage_frame + F14_SUFFIX_DELAY)
    
    elseif boot_stage == 3 and boot_program:upper() == "JSW2RUN" then
        keypost_at("*RUN\"JSW", next_stage_frame + JSW2_PREFIX_DELAY)
        if frame_num == next_stage_frame + JSW2_DIGIT_DELAY then
            print("[Atom Flop] Pressing Atom key 2")
            set_digit_key("2", true)
        elseif digit_key_down == "2" and frame_num == next_stage_frame + JSW2_DIGIT_DELAY + DIGIT_KEY_HOLD_FRAMES then
            set_digit_key("2", false)
        end
        keypost_at("RUN\"\n", next_stage_frame + JSW2_SUFFIX_DELAY)

    elseif boot_stage == 3 and has_lowercase(boot_program) then
        keypost_at("*RUN\"", next_stage_frame + F14_PREFIX_DELAY)
        start_lowercase_text(boot_program, next_stage_frame + LOWERCASE_START_DELAY)
        process_lowercase_text()
        if lowercase_done_frame ~= 0 and not lowercase_close_posted and frame_num >= lowercase_done_frame + LOWERCASE_KEY_GAP_FRAMES then
            print("[Atom Flop] Closing lowercase run command")
            emu.keypost("\"\n")
            lowercase_close_posted = true
        end
    elseif boot_stage == 3 then
        keypost_at("*RUN\"" .. boot_program .. "\"\n", next_stage_frame + F14_PREFIX_DELAY)
    end

    if boot_stage == 3 and has_lowercase(boot_program) and lowercase_close_posted and frame_num > lowercase_done_frame + 60 then
        subscription:unsubscribe()
    elseif boot_stage == 3 and not has_lowercase(boot_program) and frame_num > next_stage_frame + F14_SUFFIX_DELAY + 60 then
        if f14_key_down then set_key_1(false) end
        if digit_key_down then set_digit_key(digit_key_down, false) end
        subscription:unsubscribe()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
