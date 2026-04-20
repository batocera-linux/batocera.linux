-- aquarius_cass.lua
--
-- Mattel Aquarius cassette autoboot.
--
-- Aquarius .caq tape format:
--   [0xFF leader bytes] [0x00 marker] [6-byte filename] [0xFF inter-block] [0x00 marker] [data]
--
-- File type detection via filename in header:
--   ASCII letters  →  BASIC program  →  CLOAD, then RUN after tape stops
--   "######" (0x23 × 6)  →  raw machine code payload  →  CLOAD (auto-executes)
--
-- Most commercial games are two-part softlist entries:
--   cass1: BASIC loader (_BAS.caq, ~145 bytes)  — handled by this script
--   cass2: machine code payload (_A.caq)         — loaded automatically by the BASIC program
-- Single-part games may be pure BASIC or a standalone machine code file.

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local CAS_SCAN_BYTES = 4096

local TAPE_TYPE_BASIC   = 0
local TAPE_TYPE_MACHINE = 1

local BUTTON_PRESS_DURATION       = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_STOP_DELAY_FRAMES  = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local button    = {}
local frame_num = 0

common_autoboot.populate_buttons(button)

local function find_cassette_image()
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            return cass.filename, cass.device and cass.device.tag or ":cassette"
        end
    end
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.caq$") or fn:find("%.cas$") then
                return img.filename, img.device and img.device.tag or ":cassette"
            end
        end
    end
    return nil, ":cassette"
end

-- ── .caq header parser ────────────────────────────────────────────────────────
--
-- Structure: [0xFF... leader] [0x00 marker] [6-byte filename] [0xFF... inter-block] [0x00 data marker] [data...]
-- Filename "######" (all 0x23) indicates a raw machine code payload.
-- Any other ASCII filename indicates a BASIC program.

local function parse_caq_header(data)
    if not data or #data < 20 then return nil end

    -- Skip 0xFF leader bytes
    local i = 1
    while i <= #data and data:byte(i) == 0xFF do i = i + 1 end

    -- Expect 0x00 header marker
    if i > #data or data:byte(i) ~= 0x00 then return nil end
    i = i + 1

    -- Read 6-byte filename
    if i + 5 > #data then return nil end
    local name_bytes = {}
    for j = i, i+5 do table.insert(name_bytes, data:byte(j)) end

    -- Detect type: all 0x23 ('#') = machine code payload; otherwise BASIC
    local all_hash = true
    for _, b in ipairs(name_bytes) do
        if b ~= 0x23 then all_hash = false; break end
    end

    local filename = ""
    for _, b in ipairs(name_bytes) do
        if b >= 0x21 and b <= 0x7E then filename = filename .. string.char(b) end
    end

    if all_hash then
        print("[Aquarius Autoboot] Header: MACHINE CODE (name='######')")
        return { file_type = TAPE_TYPE_MACHINE, filename = "######" }
    else
        print(string.format("[Aquarius Autoboot] Header: BASIC  name='%s'", filename))
        return { file_type = TAPE_TYPE_BASIC, filename = filename }
    end
end

local function detect_tape_info()
    print("[Aquarius Autoboot] --- Tape type detection ---")
    local path = find_cassette_image()
    if not path then
        print("[Aquarius Autoboot] No cassette image found, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    print("[Aquarius Autoboot] Tape path: " .. path)
    local data = zip_util.read_bytes(path, CAS_SCAN_BYTES)
    if not data then
        print("[Aquarius Autoboot] Could not read tape, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local info = parse_caq_header(data)
    if info then return info end
    print("[Aquarius Autoboot] No valid header found, defaulting to BASIC.")
    return { file_type = TAPE_TYPE_BASIC, filename = "" }
end

-- ── Cassette handler (same stop-detection pattern as mc10_cass.lua) ───────────

local function create_cassette_handler(cassette_device_tag)
    local stop_frame   = 0
    local seen_playing = false
    local load_done    = false

    return function(current_frame_num, delay_frames_after_stop)
        local dev = manager.machine.cassettes[cassette_device_tag]
        if not dev then
            print("[Aquarius Autoboot] Cassette device not found: " .. cassette_device_tag)
            return false
        end

        if dev.is_stopped == false then
            manager.machine.video.throttled = false
            manager.machine.video.frameskip = 12
            seen_playing = true
        else
            manager.machine.video.throttled = true
            manager.machine.video.frameskip = 0
            if seen_playing and stop_frame == 0 then
                stop_frame = current_frame_num
                print("[Aquarius Autoboot] Cassette stop detected at frame " .. current_frame_num)
            end
        end

        if not load_done and stop_frame ~= 0 and
           current_frame_num > stop_frame + delay_frames_after_stop then
            load_done = true
            print("[Aquarius Autoboot] Cassette load complete at frame " .. current_frame_num)
            return true
        end
        return false
    end
end

local function play_cassette(cassette_tag, start_frame)
    if frame_num == start_frame then
        local dev = manager.machine.cassettes[cassette_tag]
        if dev then
            dev:play()
            print("[Aquarius Autoboot] Playing cassette at frame " .. frame_num)
        else
            print("[Aquarius Autoboot] Cassette device not found for play: " .. cassette_tag)
        end
    end
end

-- ── Boot functions ────────────────────────────────────────────────────────────

local tape_info       = nil
local cassette_tag    = ":cassette"
local cassette_handler = nil

local function boot_basic()
    -- Aquarius BASIC load sequence:
    --   1. Enter        — dismiss any initial splash
    --   2. CLOAD"name"  — BASIC sends motor-on to the cassette (MAME starts tape automatically)
    --   3. play_cassette — belt-and-suspenders: explicitly start tape in case motor signal is late
    --   4. RUN          — after tape stops, run the loaded program
    local cmd = string.format('CLOAD"%s"\n', tape_info.filename)
    common_autoboot.type_at_frame(frame_num, "\n",  100, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, cmd,   150, BUTTON_PRESS_DURATION)
    play_cassette(cassette_tag, 200)

    if cassette_handler and cassette_handler(frame_num, CASSETTE_STOP_DELAY_FRAMES) then
        emu.keypost("RUN\n")
    end
end

local function boot_machine()
    -- Machine code payload: same sequence, no RUN needed (auto-executes on load).
    common_autoboot.type_at_frame(frame_num, "\n",      100, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 150, BUTTON_PRESS_DURATION)
    play_cassette(cassette_tag, 200)

    if cassette_handler then
        cassette_handler(frame_num, CASSETTE_STOP_DELAY_FRAMES)
    end
end

-- ── Main ──────────────────────────────────────────────────────────────────────

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        common_autoboot.print_image_info()
        local _, detected_tag = find_cassette_image()
        cassette_tag    = detected_tag or ":cassette"
        cassette_handler = create_cassette_handler(cassette_tag)
        tape_info       = detect_tape_info()
    end

    common_autoboot.debug_frame_num(frame_num)

    if tape_info and tape_info.file_type == TAPE_TYPE_MACHINE then
        boot_machine()
    else
        boot_basic()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
