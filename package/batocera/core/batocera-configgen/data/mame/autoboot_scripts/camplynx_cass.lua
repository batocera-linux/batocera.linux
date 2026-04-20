-- camplynx_cass.lua
--
-- Camputers Lynx cassette autoboot with header-based type detection.
--
-- CampLynx .tap byte format:
--   0x22              opening quote
--   <filename>        ASCII string (variable length)
--   0x22              closing quote
--   0x42 ('B')        BASIC program   →  LOAD "name"\n + RUN\n after motor off
--   0x4D ('M')        machine code    →  MLOAD "name"\n (auto-runs after load)
--

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local TAP_SCAN_BYTES = 256

local TAPE_TYPE_BASIC   = 0
local TAPE_TYPE_MACHINE = 1

local BUTTON_PRESS_DURATION           = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local CASSETTE_SLOT       = 1
local CASSETTE_DEVICE_TAG = manager.machine.images:at(CASSETTE_SLOT).device.tag

local button    = {}
local frame_num = 0
common_autoboot.populate_buttons(button)

local function find_cassette_path()
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            print("[CampLynx Autoboot] Cassette device: " .. cass.filename)
            return cass.filename
        end
    end
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.tap$") or fn:find("%.cas$") or fn:find("%.wav$") then
                print("[CampLynx Autoboot] Image device cassette: " .. img.filename)
                return img.filename
            end
        end
    end
    return nil
end

-- ── CampLynx header parser ────────────────────────────────────────────────────
--
-- Format: "filename"<type_byte>...
--   0x22 ... 0x22  quoted filename
--   0x42 ('B')     BASIC
--   0x4D ('M')     machine code

local function parse_tap_header(data)
    if not data or #data < 4 then return nil end
    if data:byte(1) ~= 0x22 then return nil end

    local end_pos = nil
    for i = 2, #data do
        if data:byte(i) == 0x22 then
            end_pos = i
            break
        end
    end
    if not end_pos or end_pos + 1 > #data then return nil end

    local filename  = data:sub(2, end_pos - 1)
    local type_byte = data:byte(end_pos + 1)

    if type_byte == 0x4D then
        print(string.format("[CampLynx Autoboot] Header: MACHINE  name='%s'", filename))
        return { file_type = TAPE_TYPE_MACHINE, filename = filename }
    else
        print(string.format("[CampLynx Autoboot] Header: BASIC  name='%s'", filename))
        return { file_type = TAPE_TYPE_BASIC, filename = filename }
    end
end

local function detect_tape_info()
    print("[CampLynx Autoboot] --- Tape type detection ---")
    local path = find_cassette_path()
    if not path then
        print("[CampLynx Autoboot] No cassette found, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local data = zip_util.read_bytes(path, TAP_SCAN_BYTES)
    if not data then
        print("[CampLynx Autoboot] Could not read cassette, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local info = parse_tap_header(data)
    if info then return info end
    print("[CampLynx Autoboot] No valid header found, defaulting to BASIC.")
    return { file_type = TAPE_TYPE_BASIC, filename = "" }
end

-- ── Boot functions ────────────────────────────────────────────────────────────

local cassette_handler = common_autoboot.create_cassette_handler(CASSETTE_DEVICE_TAG)
local tape_info        = nil

local function boot_basic()
    common_autoboot.type_at_frame(frame_num, 'LOAD "' .. tape_info.filename .. '"\n', 100, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 200)

    if cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES) then
        emu.keypost("RUN\n")
    end
end

local function boot_machine()
    -- MLOAD auto-runs after loading; no post-load command needed.
    common_autoboot.type_at_frame(frame_num, 'MLOAD "' .. tape_info.filename .. '"\n', 100, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 200)

    cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)
end

-- ── Main ──────────────────────────────────────────────────────────────────────

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        common_autoboot.print_image_info()
        tape_info = detect_tape_info()
    end

    common_autoboot.debug_frame_num(frame_num)

    if tape_info and tape_info.file_type == TAPE_TYPE_MACHINE then
        boot_machine()
    else
        boot_basic()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
