-- trs80_cass.lua

local zip_util = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

-- ── Configuration ─────────────────────────────────────────────────────────────
local CAS_SCAN_BYTES     = 4096   -- bytes to read from CAS for header search

-- ── Tape type constants (XRoar tape.h) ────────────────────────────────────────
local TAPE_TYPE_BASIC   = 0   -- CLOAD\r + RUN\r
local TAPE_TYPE_DATA    = 1   -- no autorun
local TAPE_TYPE_MACHINE = 2   -- CLOADM\r + EXEC\r
 
-- ── State machine ─────────────────────────────────────────────────────────────
local STATE_IDLE        = 0
local STATE_BOOTING     = 1
local STATE_TYPING_LOAD = 2
local STATE_WAITING     = 3
local STATE_TYPING_RUN  = 4
local STATE_DONE        = 5
 
-- ── Runtime state ─────────────────────────────────────────────────────────────
local state            = STATE_IDLE
local frame_counter    = 0
local tape_file_type   = nil
local load_command     = nil
local run_command      = nil
local cmd_queue        = {}
local load_start_frame = 0
 
 
-- ── CAS header parser ─────────────────────────────────────────────────────────
 
--- Scan a raw Lua byte-string for a valid CoCo CAS file header.
--- Mirrors XRoar's tape_file_next() / tape_autorun() in tape.c.
--- Returns the file-type byte (0/1/2) on success, nil if not found.
local function parse_cas_header(data)
    if not data or #data < 20 then return nil end
 
    local i          = 1
    local saw_leader = false
 
    while i <= #data do
        local b = data:byte(i)
 
        if b == 0x55 then
            saw_leader = true
            i = i + 1
 
        elseif b == 0x3C and saw_leader then
            -- Sync byte after leader sequence → header block follows
            local base = i + 1
            if base + 16 > #data then return nil end
 
            local block_type = data:byte(base)
            local block_size = data:byte(base + 1)
 
            if block_type == 0x00 and block_size >= 15 then
                local dstart = base + 2
                if dstart + 8 <= #data then
                    local file_type = data:byte(dstart + 8)
                    -- Log the filename (bytes 0-7 of block data)
                    local fname = ""
                    for fi = 0, 7 do
                        local c = data:byte(dstart + fi)
                        if c and c ~= 0x20 and c ~= 0x00 then
                            fname = fname .. string.char(c)
                        end
                    end
                    print(string.format(
                        "[CoCo Autoboot] CAS header: file='%s'  type=%d",
                        fname, file_type))
                    return file_type
                end
            else
                -- Malformed block after sync; keep scanning
                saw_leader = false
                i = i + 1
            end
 
        else
            saw_leader = false
            i = i + 1
        end
    end
 
    return nil
end
 
 
-- ── Cassette path discovery ───────────────────────────────────────────────────
 
--- Find the mounted cassette image filename via MAME's image API.
local function find_cassette_path()
    -- First try the specific cassette device enumerator
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            print("[CoCo Autoboot] Cassette device: " .. cass.filename)
            return cass.filename
        end
    end
    -- Fallback: scan all image devices for .cas extension
    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.cas$") then
                print("[CoCo Autoboot] Image device (.cas): " .. img.filename)
                return img.filename
            end
        end
    end
    return nil
end
 
--- Top-level detection.
local function detect_tape_type()
    print("[CoCo Autoboot] --- Tape type detection ---")
 
    local path = find_cassette_path()
    if not path then
        print("[CoCo Autoboot] No cassette image found.")
        return nil
    end
    print("[CoCo Autoboot] Path: " .. path)
 
    local data = zip_util.read_bytes(path, CAS_SCAN_BYTES)
    if not data then
        print("[CoCo Autoboot] Could not read CAS data — defaulting to BASIC.")
        return TAPE_TYPE_BASIC
    end
 
    local ft = parse_cas_header(data)
    if ft ~= nil then return ft end
 
    print("[CoCo Autoboot] No valid CAS header found — defaulting to BASIC.")
    return TAPE_TYPE_BASIC
end



-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

common_autoboot.populate_buttons(button)

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function boot_default_basic(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 100, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 200)

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if cassette_load_done then
        emu.keypost('RUN\n')
    end
end

local function boot_default_machine(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "CLOADM:EXEC\n", 100, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 200)

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

end

local function create_boot_type_1_sequence(title_to_type) -- New name for clarity
    return function(cassette_handler_arg) -- This is the function that process_frame will call every frame
        common_autoboot.type_at_frame(frame_num, "L\n", 100)
        common_autoboot.type_at_frame(frame_num, "\n", 200)
        common_autoboot.type_at_frame(frame_num, "SYSTEM\n", 300)
        common_autoboot.type_at_frame(frame_num, title_to_type .. "\n", 400)
        common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 500)

        local cassette_load_done = cassette_handler_arg(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

        if cassette_load_done then
            emu.keypost('/\n')
        end
    end
end

local function create_boot_type_2_sequence() -- New name for clarity
    return function(cassette_handler_arg) -- This is the function that process_frame will call every frame
        common_autoboot.type_at_frame(frame_num, "L\n", 100)
        common_autoboot.type_at_frame(frame_num, "\n", 200)
        common_autoboot.type_at_frame(frame_num, "CLOAD\n", 300)
        common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 400)

        local cassette_load_done = cassette_handler_arg(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

        if cassette_load_done then
            emu.keypost('RUN\n')
        end
    end
end

local function boot_dtrap(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "L\n", 100, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "\n", 200, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "32640\n", 300, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 400, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 500)

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if cassette_load_done then
        emu.keypost('RUN\n')
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(1).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    adv03 = create_boot_type_1_sequence("MISSIO"),
    adv10 = create_boot_type_1_sequence("SAVAGE"),
    android = create_boot_type_2_sequence(),
    baccarat = create_boot_type_2_sequence(),
    backgamm = create_boot_type_2_sequence(),
    blakjack = create_boot_type_2_sequence(),
    chess = create_boot_type_1_sequence("SARGON"),
    colliss = create_boot_type_2_sequence(),
    cosmic = create_boot_type_1_sequence("COSMIC"),
    craps = create_boot_type_2_sequence(),
    dddd = create_boot_type_1_sequence("DANDEM"),
    defense = create_boot_type_2_sequence("DEFENS"),
    dtrap = boot_dtrap,
    eliza = create_boot_type_1_sequence("ELIZA"),
    env = create_boot_type_1_sequence("ENV"),
    escape = create_boot_type_1_sequence("ESCAPE"),
    galaxy1 = create_boot_type_1_sequence("GALAXY"),
    galaxy2 = create_boot_type_1_sequence("GALAXY"),
    headon = create_boot_type_1_sequence("HEADON"),
    heliko = create_boot_type_1_sequence("HELIKO"),
    hoppy = create_boot_type_1_sequence("HG"),
    invaders = create_boot_type_1_sequence("INVADE"),
    invasion = create_boot_type_1_sequence("INVADE"),
    keno = create_boot_type_2_sequence(),
    kinghill = create_boot_type_1_sequence("R"),
    meteor2 = create_boot_type_1_sequence("METEOR"),
    microply = create_boot_type_2_sequence(),
    penetr = create_boot_type_1_sequence("PENETR"),
    pinball = create_boot_type_2_sequence(),
    pyrmd = create_boot_type_1_sequence("PYRMD"),
    qwatson = create_boot_type_2_sequence(),
    robot = create_boot_type_1_sequence("ROBOT"),
    roulette = create_boot_type_2_sequence(),
    scarfman = create_boot_type_1_sequence("SCARFM"),
    scripsit = create_boot_type_1_sequence("SCRIPS"),
    seadragon = create_boot_type_1_sequence("SEADRA"),
    slot = create_boot_type_2_sequence(),
    spaceinv = create_boot_type_1_sequence("INVADE"),
    spcinv = create_boot_type_1_sequence("SPCINV"),
    spcwarp = create_boot_type_1_sequence("SPWAR"),
    starfi = create_boot_type_1_sequence("STARFI"),
    starsm = create_boot_type_1_sequence("STARSM"),
    startrek = create_boot_type_2_sequence(),
    starwar = create_boot_type_2_sequence(),
    swamp = create_boot_type_1_sequence("SWAMP"),
    taipan = create_boot_type_2_sequence(),
    trollcru = create_boot_type_2_sequence(),
    wheel = create_boot_type_2_sequence(),
    zchess = create_boot_type_1_sequence("ZCHESS"),
    
    ["default_basic"] = boot_default_basic,
    ["default_machine"] = boot_default_machine,
}

-- --- Cassette Loading Handler Setup ---
local cassette_handler = common_autoboot.create_cassette_handler(":cassette") 

-- MAME machine frame notification callback
local function process_frame()
    frame_num = frame_num + 1

    -- Initial setup/info display at frame 1
    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        emu.print_info("Loaded Software Name (from image filename): " .. current_software_name)

        -- Determine which profile will be used 
        if boot_sequences[current_software_name] then
            emu.print_info("--- Booting using game specific profile: " .. current_software_name .. " ---")
        else
            emu.print_info("--- Booting using default profile ---")
        end        

        tape_file_type = detect_tape_type()
    end

    -- --- Print current frame number every 100 frames ---
    if frame_num % 100 == 0 then -- The modulo operator (%) gives the remainder of a division
        emu.print_info("Current Frame: " .. frame_num)
    end    

    -- Execute the relevant boot sequence based on the loaded software
    local boot_function = boot_sequences[current_software_name]


    if not boot_function then -- If specific function not found

        if tape_file_type == TAPE_TYPE_MACHINE then
            boot_function = boot_sequences["default_machine"] -- Assign the default function
        elseif tape_file_type == TAPE_TYPE_BASIC then
            boot_function = boot_sequences["default_basic"] -- Assign the default function
        else
            boot_function = boot_sequences["default_basic"] -- Assign the default function
        end
    end

    if boot_function then
        boot_function(cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)
