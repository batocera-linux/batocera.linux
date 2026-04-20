-- cgenie_cass.lua
--
-- Colour Genie cassette autoboot with header-based type detection.
--
-- CGenie .cas byte format (after optional 36-byte ASCII text header):
--   0x66              sync byte
--   0x55              header/name block marker  →  machine-code program
--   [0..5]            filename (6 bytes ASCII, 0x20-padded)
--   0x3C              data block follows
--   ...
--
--   0x66              sync byte
--   <anything≠0x55>   BASIC tokenised data follows  →  BASIC program
--
-- Boot sequences:
--   BASIC       → \n · CLOAD\n · play · RUN\n after motor off
--   machine code→ \n · SYSTEM\n · <filename>\n · play · /\n after motor off

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local CAS_SCAN_BYTES = 4096

local TAPE_TYPE_BASIC   = 0
local TAPE_TYPE_DATA    = 1
local TAPE_TYPE_MACHINE = 2

local BUTTON_PRESS_DURATION           = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local button    = {}
local frame_num = 0
common_autoboot.populate_buttons(button)

local function find_cassette_path()
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            print("[CGenie Autoboot] Cassette device: " .. cass.filename)
            return cass.filename
        end
    end
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.cas$") or fn:find("%.wav$") then
                print("[CGenie Autoboot] Image device cassette: " .. img.filename)
                return img.filename
            end
        end
    end
    return nil
end

-- ── CGenie header parser ──────────────────────────────────────────────────────
--
-- Scan for the 0x66 sync byte.  The byte immediately following it determines
-- the file type:
--   0x55 → machine-code (SYSTEM) program; next 6 bytes are the filename.
--   other → BASIC (CLOAD) program; no filename needed.

local function parse_cgenie_header(data)
    if not data or #data < 4 then return nil end

    for i = 1, #data - 2 do
        if data:byte(i) == 0x66 then
            local next_byte = data:byte(i + 1)

            if next_byte == 0x55 then
                -- Machine-code header: read 6-byte filename
                if i + 7 > #data then return nil end
                local raw = {}
                for j = 0, 5 do
                    raw[j + 1] = data:byte(i + 2 + j)
                end
                -- Strip trailing spaces and NULs to get the name SYSTEM expects
                local name_end = 6
                while name_end >= 1 and (raw[name_end] == 0x20 or raw[name_end] == 0x00) do
                    name_end = name_end - 1
                end
                local filename = ""
                for j = 1, name_end do
                    filename = filename .. string.char(raw[j])
                end
                print(string.format("[CGenie Autoboot] Header: MACHINE  name='%s'", filename))
                return { file_type = TAPE_TYPE_MACHINE, filename = filename }
            else
                -- No name block → BASIC program
                print("[CGenie Autoboot] Header: BASIC")
                return { file_type = TAPE_TYPE_BASIC, filename = "" }
            end
        end
    end

    return nil
end

local function detect_tape_info()
    print("[CGenie Autoboot] --- Tape type detection ---")
    local path = find_cassette_path()
    if not path then
        print("[CGenie Autoboot] No cassette found, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local data = zip_util.read_bytes(path, CAS_SCAN_BYTES)
    if not data then
        print("[CGenie Autoboot] Could not read cassette, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, filename = "" }
    end
    local info = parse_cgenie_header(data)
    if info then return info end
    print("[CGenie Autoboot] No valid header found, defaulting to BASIC.")
    return { file_type = TAPE_TYPE_BASIC, filename = "" }
end

-- ── Boot functions ────────────────────────────────────────────────────────────

local cassette_handler = common_autoboot.create_cassette_handler(":cassette")
local tape_info        = nil

local function boot_basic()
    common_autoboot.type_at_frame(frame_num, "\n",      50,  BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 200, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 300)

    if cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES) then
        emu.keypost("RUN\n")
    end
end

local function boot_machine()
    -- SYSTEM prompts "*? " for the tape name, then loads from tape,
    -- then prompts "*/ " for the start address; "/" runs from default.
    common_autoboot.type_at_frame(frame_num, "\n",                       50,  BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "SYSTEM\n",                 150, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, tape_info.filename .. "\n", 200, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 300)

    if cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES) then
        emu.keypost("/\n")
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

    if tape_info and tape_info.file_type == TAPE_TYPE_MACHINE then
        boot_machine()
    else
        boot_basic()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
