-- msx1_cass.lua
--
-- MSX1 cassette autoboot with header-based file-type detection.
--
-- MSX .cas block layout:
--   Offset  0-7  : sync header  1F A6 DE BA CC 13 7D 74
--   Offset  8-17 : type indicator (10 identical bytes)
--                    0xD3 x10  →  tokenised BASIC (CSAVE)  →  CLOAD, then RUN after motor off
--                    0xD0 x10  →  binary / machine code (BSAVE)  →  BLOAD"CAS:",R
--                    0xEA x10  →  ASCII BASIC (SAVE)  →  RUN"CAS:"
--   Offset 18-23 : filename (6 ASCII bytes, space-padded)
--
-- Load commands (ref: http://www.msxblue.com/manual/runningcas_c.htm):
--   CSAVE files (0xD3) : CLOAD  →  RUN after motor off
--   BSAVE files (0xD0) : BLOAD"CAS:",R  (auto-executes, no post-command)
--   SAVE  files (0xEA) : LOAD"CAS:"  →  RUN after motor off
--     (RUN"CAS:" fails on MSX2 DISK-BASIC: it doesn't block for the motor signal)
--
-- Reference: MSX2 Technical Handbook chapter 5a; blueMSX source (ducasp/blueMSX).

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local CAS_SCAN_BYTES = 4096

local TAPE_TYPE_BASIC   = 0
local TAPE_TYPE_MACHINE = 1
local TAPE_TYPE_ASCII   = 2

local MSX_CAS_SYNC = { 0x1F, 0xA6, 0xDE, 0xBA, 0xCC, 0x13, 0x7D, 0x74 }

local BUTTON_PRESS_DURATION           = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local CASSETTE_DEVICE_TAG = ":cassette"

local button    = {}
local frame_num = 0
common_autoboot.populate_buttons(button)

local function find_cassette_path()
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            print("[MSX1 Cass Autoboot] Cassette device: " .. cass.filename)
            return cass.filename
        end
    end
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.cas$") or fn:find("%.wav$") then
                print("[MSX1 Cass Autoboot] Image device cassette: " .. img.filename)
                return img.filename
            end
        end
    end
    return nil
end

-- ── MSX .cas header parser ────────────────────────────────────────────────────
--
-- Scan for the 8-byte sync sequence, then inspect the 10 type bytes that follow.

local function find_sync(data)
    if not data or #data < 18 then return nil end
    for i = 1, #data - 17 do
        local ok = true
        for j = 1, 8 do
            if data:byte(i + j - 1) ~= MSX_CAS_SYNC[j] then
                ok = false; break
            end
        end
        if ok then return i end
    end
    return nil
end

local function parse_cas_header(data)
    local sync_pos = find_sync(data)
    if not sync_pos then return nil end

    -- 10 type-indicator bytes follow the 8-byte sync
    local type_base = sync_pos + 8
    if type_base + 9 > #data then return nil end

    local type_byte = data:byte(type_base)
    local uniform = true
    for i = 1, 9 do
        if data:byte(type_base + i) ~= type_byte then
            uniform = false; break
        end
    end
    if not uniform then return nil end

    -- 6-byte filename follows the type indicator
    local name_base = type_base + 10
    local filename  = ""
    if name_base + 5 <= #data then
        local chars = {}
        for i = 0, 5 do
            local c = data:byte(name_base + i)
            if c and c ~= 0x00 and c ~= 0x20 then
                table.insert(chars, string.char(c))
            end
        end
        filename = table.concat(chars)
    end

    if type_byte == 0xD3 then
        print(string.format("[MSX1 Cass Autoboot] Header: BASIC  name='%s'", filename))
        return { file_type = TAPE_TYPE_BASIC, filename = filename }
    elseif type_byte == 0xD0 then
        print(string.format("[MSX1 Cass Autoboot] Header: MACHINE  name='%s'", filename))
        return { file_type = TAPE_TYPE_MACHINE, filename = filename }
    elseif type_byte == 0xEA then
        print(string.format("[MSX1 Cass Autoboot] Header: ASCII  name='%s'", filename))
        return { file_type = TAPE_TYPE_ASCII, filename = filename }
    end

    print(string.format("[MSX1 Cass Autoboot] Unknown type byte 0x%02X, defaulting to BASIC.", type_byte))
    return { file_type = TAPE_TYPE_BASIC, filename = filename }
end

local function detect_tape_info()
    print("[MSX1 Cass Autoboot] --- Tape type detection ---")
    local path = find_cassette_path()
    if not path then
        print("[MSX1 Cass Autoboot] No cassette found, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local data = zip_util.read_bytes(path, CAS_SCAN_BYTES)
    if not data then
        print("[MSX1 Cass Autoboot] Could not read cassette, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local info = parse_cas_header(data)
    if info then return info end
    print("[MSX1 Cass Autoboot] No valid header found, defaulting to BASIC.")
    return { file_type = TAPE_TYPE_BASIC, filename = "" }
end

-- ── Boot functions ────────────────────────────────────────────────────────────

local cassette_handler = common_autoboot.create_cassette_handler(CASSETTE_DEVICE_TAG)
local tape_info        = nil

local function boot_basic()
    -- Tokenised BASIC saved with CSAVE (0xD3): CLOAD, then RUN after motor off
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 150, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 250)

    if cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES) then
        emu.keypost("RUN\n")
    end
end

local function boot_machine()
    -- Binary saved with BSAVE (0xD0): BLOAD"CAS:",R — auto-executes, no post-load command
    common_autoboot.type_at_frame(frame_num, 'BLOAD"CAS:",R\n', 150, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 250)

    cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)
end

local function boot_ascii()
    -- ASCII BASIC saved with SAVE"CAS:",A (0xEA): LOAD"CAS:" waits for motor like CLOAD,
    -- then RUN after tape stops. RUN"CAS:" returns "bad file name" on MSX2 DISK-BASIC
    -- because it doesn't block for the motor signal before timing out.
    common_autoboot.type_at_frame(frame_num, 'LOAD"CAS:"\n', 150, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 250)

    if cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES) then
        emu.keypost("RUN\n")
    end
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

    if tape_info.file_type == TAPE_TYPE_MACHINE then
        boot_machine()
    elseif tape_info.file_type == TAPE_TYPE_ASCII then
        boot_ascii()
    else
        boot_basic()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
