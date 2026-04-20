-- sorcerer_cass.lua

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

common_autoboot.populate_buttons(button)

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function boot_default(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 300, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 400)

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if cassette_load_done then
        emu.keypost('RUN\n')
    end
end

local function create_boot_type_1_sequence() 
    return function(cassette_handler_arg)
        common_autoboot.type_at_frame(frame_num, "BYE\n", 300)
        common_autoboot.type_at_frame(frame_num, "LOG\n", 400)
        common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 500)

        local cassette_load_done = cassette_handler_arg(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

        if cassette_load_done then
            -- emu.keypost('/\n')
        end
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(3).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    adv1 = create_boot_type_1_sequence(),
    adv2 = create_boot_type_1_sequence(),
    adv3 = create_boot_type_1_sequence(),
    adv4 = create_boot_type_1_sequence(),
    adv5 = create_boot_type_1_sequence(),
    adv6 = create_boot_type_1_sequence(),
    adv7 = create_boot_type_1_sequence(),
    adv8 = create_boot_type_1_sequence(),
    adv9 = create_boot_type_1_sequence(),
    amaze = create_boot_type_1_sequence(),
    apatrol = create_boot_type_1_sequence(),
    arith = create_boot_type_1_sequence(),
    arrow = create_boot_type_1_sequence(),
    arrow2 = create_boot_type_1_sequence(),
    ast = create_boot_type_1_sequence(),
    aster = create_boot_type_1_sequence(),
    astro = create_boot_type_1_sequence(),
    atc = create_boot_type_1_sequence(),
    atc1 = create_boot_type_1_sequence(),
    biochart = create_boot_type_1_sequence(),
    biorhythm = create_boot_type_1_sequence(),
    blackj = create_boot_type_1_sequence(),
    cadas = create_boot_type_1_sequence(),
    char = create_boot_type_1_sequence(),
    chess1 = create_boot_type_1_sequence(),
    chess2 = create_boot_type_1_sequence(),
    chomp = create_boot_type_1_sequence(),
    com48 = create_boot_type_1_sequence(),
    cosmc = create_boot_type_1_sequence(),
    crash = create_boot_type_1_sequence(),
    debug = create_boot_type_1_sequence(),
    defcm = create_boot_type_1_sequence(),
    dfndr = create_boot_type_1_sequence(),
    disas2 = create_boot_type_1_sequence(),
    dterm = create_boot_type_1_sequence(),
    dybug = create_boot_type_1_sequence(),
    ezy = create_boot_type_1_sequence(),
    fgam = create_boot_type_1_sequence(),
    flip = create_boot_type_1_sequence(),
    flite = create_boot_type_1_sequence(),
    galax = create_boot_type_1_sequence(),
    galx = create_boot_type_1_sequence(),
    grotnik = create_boot_type_1_sequence(),
    homerun = create_boot_type_1_sequence(),
    hpad = create_boot_type_1_sequence(),
    interceptor = create_boot_type_1_sequence(),
    invad2 = create_boot_type_1_sequence(),
    invaders = create_boot_type_1_sequence(),
    kalid = create_boot_type_1_sequence(),
    killerg = create_boot_type_1_sequence(),
    kilo = create_boot_type_1_sequence(),
    kilopede = create_boot_type_1_sequence(),
    l2x = create_boot_type_1_sequence(),
    landarc = create_boot_type_1_sequence(),
    ldg = create_boot_type_1_sequence(),
    magicmaze = create_boot_type_1_sequence(),
    midas = create_boot_type_1_sequence(),
    minva = create_boot_type_1_sequence(),
    misil = create_boot_type_1_sequence(),
    mmind = create_boot_type_1_sequence(),
    munch = create_boot_type_1_sequence(),
    nike2 = create_boot_type_1_sequence(),
    robot = create_boot_type_1_sequence(),
    spider = create_boot_type_1_sequence(),
    starf = create_boot_type_1_sequence(),
    sword = create_boot_type_1_sequence(),
    wumpus = create_boot_type_1_sequence(),
    zetu = create_boot_type_1_sequence(),

    ["default"] = boot_default,
}

-- --- Cassette Loading Handler Setup ---
local cassette_handler = common_autoboot.create_cassette_handler(":cassette1") 

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
    end

    --- Print current frame number every 100 frames ---
    if frame_num % 100 == 0 then -- The modulo operator (%) gives the remainder of a division
        emu.print_info("Current Frame: " .. frame_num)
    end    

    -- Execute the relevant boot sequence based on the loaded software
    local boot_function = boot_sequences[current_software_name]

    if not boot_function then -- If specific function not found
        boot_function = boot_sequences["default"] -- Assign the default function
    end

    if boot_function then
        boot_function(cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)