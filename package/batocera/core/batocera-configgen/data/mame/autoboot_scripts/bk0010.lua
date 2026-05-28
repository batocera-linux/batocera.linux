-- bk0010.lua

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

-- --- Load butons ---
common_autoboot.populate_buttons(button)

-- --- Print Info ---
common_autoboot.print_image_info()
-- common_autoboot.print_buttons(button)

-- --- Cassette Loading Handler Setup ---
local CASSETTE_SLOT = 1
local CASSETTE_DEVICE_TAG = manager.machine.images:at(CASSETTE_SLOT).device.tag
local cassette_handler = common_autoboot.create_cassette_handler(CASSETTE_DEVICE_TAG) 


-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = 100 -- common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function create_boot_default_sequence(frame_num, cassette_monitor_func, title_to_type) -- 'cassette_monitor_func' is the per-frame callable handler
    local sequence_state = 0
    -- Define states for clarity
    local STATES = {
        INIT_PRE_LOAD_ACTIONS = 0, -- Initial actions before CLOAD/PLAY
        PLAY_CASS_INITIATED = 1,   -- CLOAD/PLAY commands sent, waiting for motor to spin up
        LOADING_CASS = 2,          -- Cassette motor is ON, monitoring for completion
        CASS_LOAD_DONE = 3,        -- Cassette has finished loading, waiting for post-load actions
        POST_LOAD_ACTIONS = 4,     -- Executing actions after cassette load
        COMPLETE = 5               -- Sequence finished
    }
    
    local post_load_start_frame = 0 -- Frame at which post-load actions began

    return function(current_frame_num) -- This inner function runs every frame
        -- Always call cassette_monitor_func once we are in a state where loading should be active.
        -- This ensures continuous monitoring, throttling, and detection of load completion.
        if sequence_state >= STATES.LOADING_CASS and sequence_state < STATES.CASS_LOAD_DONE then
            local cassette_load_done = cassette_monitor_func(current_frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)
            if cassette_load_done then
                sequence_state = STATES.CASS_LOAD_DONE -- Transition directly to CASS_LOAD_DONE
                post_load_start_frame = current_frame_num -- Mark start for relative timing of post-actions
                emu.print_info("Boot Default: Cassette loading is complete (triggered by handler). Transitioning to post-load actions.")
                return -- Exit early for this frame after state change, to prevent double-execution
            end
        end

        -- --- State Machine Logic ---
        if sequence_state == STATES.INIT_PRE_LOAD_ACTIONS then
            -- Schedule initial pre-load actions
            common_autoboot.type_at_frame(current_frame_num, "MO\n", 100)
            common_autoboot.type_at_frame(current_frame_num, "M\n", 200)
            common_autoboot.type_at_frame(current_frame_num, title_to_type .. "\n", 300)
            common_autoboot.play_cassette_at_frame(current_frame_num, CASSETTE_DEVICE_TAG, 400)
            
            -- Transition to PLAY_CASS_INITIATED after these actions are scheduled (at the last target frame or beyond)
            if current_frame_num >= 350 then
                sequence_state = STATES.PLAY_CASS_INITIATED
                emu.print_info("Boot Default: Pre-load actions scheduled. Waiting for cassette motor to engage.")
            end
            
        elseif sequence_state == STATES.PLAY_CASS_INITIATED then
            -- Wait for the cassette motor to actually spin up
            local cassette_device = manager.machine.cassettes[CASSETTE_DEVICE_TAG]
            if cassette_device and cassette_device.motor_state == true then
                sequence_state = STATES.LOADING_CASS
                emu.print_info("Boot Default: Cassette motor confirmed ON. Beginning continuous monitoring.")
            end

        -- If sequence_state becomes CASS_LOAD_DONE (from the monitor above), this block is skipped,
        -- and the logic will fall through to the next `elseif` for POST_LOAD_ACTIONS in the subsequent frame.

        elseif sequence_state == STATES.CASS_LOAD_DONE then
            -- This state is primarily a transition point.
            -- The 'RUN' command is NOT issued here. It's issued by the cassette_monitor_func internally.
            -- We transition immediately to POST_LOAD_ACTIONS after load is detected.
            sequence_state = STATES.POST_LOAD_ACTIONS
            emu.print_info("Boot Default: Transitioning to post-load actions.")

        elseif sequence_state == STATES.POST_LOAD_ACTIONS then
            -- --- Actions to perform AFTER cassette load is done ---
            -- Use `post_load_start_frame` for relative timing
            common_autoboot.type_at_frame(current_frame_num, "S\n", post_load_start_frame + 50, 1)

            -- Check if all post-load actions are completed
            if current_frame_num >= post_load_start_frame + 100 + BUTTON_PRESS_DURATION then
                sequence_state = STATES.COMPLETE
                emu.print_info("Boot Default: All post-load actions completed. Sequence finished.")
            end

        elseif sequence_state == STATES.COMPLETE then
            -- Do nothing, sequence is finished.
        end
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(CASSETTE_SLOT).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    aljur = create_boot_default_sequence(frame_num, cassette_handler, "ALJUR .COD"),
    antix = create_boot_default_sequence(frame_num, cassette_handler, "Antix"),
    apple = create_boot_default_sequence(frame_num, cassette_handler, "Apple"),
    arkano = create_boot_default_sequence(frame_num, cassette_handler, "Arkano"),
    arkanoid = create_boot_default_sequence(frame_num, cassette_handler, "Arkanoid"),
    asprekl = create_boot_default_sequence(frame_num, cassette_handler, "Asp_rekl"),
    ass = create_boot_default_sequence(frame_num, cassette_handler, "Ass"),
    ass2 = create_boot_default_sequence(frame_num, cassette_handler, "Ass2"),
    astrdrom = create_boot_default_sequence(frame_num, cassette_handler, "Astrdrom"),
    baby = create_boot_default_sequence(frame_num, cassette_handler, "Baby"),
    bally = create_boot_default_sequence(frame_num, cassette_handler, "Bally"),
    bapple = create_boot_default_sequence(frame_num, cassette_handler, "Bapple"),
    barb = create_boot_default_sequence(frame_num, cassette_handler, "Barb"),
    barbar = create_boot_default_sequence(frame_num, cassette_handler, "Barbar"),
    barman = create_boot_default_sequence(frame_num, cassette_handler, "Barman"),
    batiskaf = create_boot_default_sequence(frame_num, cassette_handler, "Batiskaf"),
    bigchess = create_boot_default_sequence(frame_num, cassette_handler, "Bigchess"),
    bil = create_boot_default_sequence(frame_num, cassette_handler, "Bil"),
    billiard = create_boot_default_sequence(frame_num, cassette_handler, "BILLIARD"),
    biowar = create_boot_default_sequence(frame_num, cassette_handler, "Biowar"),
    bkdemo = create_boot_default_sequence(frame_num, cassette_handler, "BKDEMO"),
    bkpack = create_boot_default_sequence(frame_num, cassette_handler, "Bkpack"),
    blcout = create_boot_default_sequence(frame_num, cassette_handler, "Blcout"),
    blockout = create_boot_default_sequence(frame_num, cassette_handler, "BLOCKOUT"),
    bolde2 = create_boot_default_sequence(frame_num, cassette_handler, "Bolde2"),
    bolder2 = create_boot_default_sequence(frame_num, cassette_handler, "Bolder2"),
    bolder3 = create_boot_default_sequence(frame_num, cassette_handler, "Bolder3"),
    bomb4 = create_boot_default_sequence(frame_num, cassette_handler, "Bomb4"),
    breach = create_boot_default_sequence(frame_num, cassette_handler, "breach"),
    ['break'] = create_boot_default_sequence(frame_num, cassette_handler, "Break"),
    breaking = create_boot_default_sequence(frame_num, cassette_handler, "Breaking"),
    brhouse = create_boot_default_sequence(frame_num, cassette_handler, "Brhouse"),
    bubbler = create_boot_default_sequence(frame_num, cassette_handler, "Bubbler"),
    bubler = create_boot_default_sequence(frame_num, cassette_handler, "Bubler"),
    cache = create_boot_default_sequence(frame_num, cassette_handler, "Cache"),
    cave = create_boot_default_sequence(frame_num, cassette_handler, "Cave"),
    cavedoc = create_boot_default_sequence(frame_num, cassette_handler, "Cave_doc"),
    caveman = create_boot_default_sequence(frame_num, cassette_handler, "Cave_man"),
    caveres = create_boot_default_sequence(frame_num, cassette_handler, "Cave_res"),
    chaser = create_boot_default_sequence(frame_num, cassette_handler, "Chaser"),
    checkers = create_boot_default_sequence(frame_num, cassette_handler, "Checkers"),
    chess07 = create_boot_default_sequence(frame_num, cassette_handler, "Chess07"),
    chess1 = create_boot_default_sequence(frame_num, cassette_handler, "Chess1"),
    chess2 = create_boot_default_sequence(frame_num, cassette_handler, "Chess2"),
    chess3 = create_boot_default_sequence(frame_num, cassette_handler, "Chess3"),
    chess4 = create_boot_default_sequence(frame_num, cassette_handler, "Chess4"),
    circler = create_boot_default_sequence(frame_num, cassette_handler, "CIRCLER"),
    columns = create_boot_default_sequence(frame_num, cassette_handler, "Columns"),
    columns2 = create_boot_default_sequence(frame_num, cassette_handler, "Columns2"),
    comic = create_boot_default_sequence(frame_num, cassette_handler, "Comic"),
    cosmic = create_boot_default_sequence(frame_num, cassette_handler, "COSMIC"),
    cosmicb = create_boot_default_sequence(frame_num, cassette_handler, "Cosmic_b"),
    courier = create_boot_default_sequence(frame_num, cassette_handler, "Courier"),
    covox = create_boot_default_sequence(frame_num, cassette_handler, "covox"),
    crack = create_boot_default_sequence(frame_num, cassette_handler, "Crack"),
    dama = create_boot_default_sequence(frame_num, cassette_handler, "Dama"),
    demsl = create_boot_default_sequence(frame_num, cassette_handler, "Demsl"),
    demsl1 = create_boot_default_sequence(frame_num, cassette_handler, "Demsl1"),
    demsl2 = create_boot_default_sequence(frame_num, cassette_handler, "Demsl2"),
    demsl3 = create_boot_default_sequence(frame_num, cassette_handler, "Demsl3"),
    desan = create_boot_default_sequence(frame_num, cassette_handler, "Desan"),
    desandoc = create_boot_default_sequence(frame_num, cassette_handler, "Desandoc"),
    desant = create_boot_default_sequence(frame_num, cassette_handler, "Desant"),
    diamond = create_boot_default_sequence(frame_num, cassette_handler, "Diamond"),
    digger = create_boot_default_sequence(frame_num, cassette_handler, "Digger"),
    divers3 = create_boot_default_sequence(frame_num, cassette_handler, "Divers3"),
    dragon = create_boot_default_sequence(frame_num, cassette_handler, "DRAGON.BIN"),
    flier = create_boot_default_sequence(frame_num, cassette_handler, "FLIER"),
    font = create_boot_default_sequence(frame_num, cassette_handler, "FONT"),
    hobbitovl = create_boot_default_sequence(frame_num, cassette_handler, "HOBBIT.OVL"),
    hobbit = create_boot_default_sequence(frame_num, cassette_handler, "HOBBIT"),
    horror = create_boot_default_sequence(frame_num, cassette_handler, "Horror"),
    horrors = create_boot_default_sequence(frame_num, cassette_handler, "Horror_s"),
    house1 = create_boot_default_sequence(frame_num, cassette_handler, "House1"),
    house2 = create_boot_default_sequence(frame_num, cassette_handler, "House2"),
    indjon = create_boot_default_sequence(frame_num, cassette_handler, "Indjon"),
    jetman = create_boot_default_sequence(frame_num, cassette_handler, "Jetman"),
    joebla = create_boot_default_sequence(frame_num, cassette_handler, "Joebla"),
    john = create_boot_default_sequence(frame_num, cassette_handler, "John"),
    johnny = create_boot_default_sequence(frame_num, cassette_handler, "Johnny"),
    jokey = create_boot_default_sequence(frame_num, cassette_handler, "Jokey"),
    jones = create_boot_default_sequence(frame_num, cassette_handler, "Jones"),
    jones1 = create_boot_default_sequence(frame_num, cassette_handler, "Jones1"),
    jones2 = create_boot_default_sequence(frame_num, cassette_handler, "Jones2"),
    jones3 = create_boot_default_sequence(frame_num, cassette_handler, "Jones3"),
    jungle = create_boot_default_sequence(frame_num, cassette_handler, "Jungle"),
    karado = create_boot_default_sequence(frame_num, cassette_handler, "Karado"),
    karate = create_boot_default_sequence(frame_num, cassette_handler, "Karate"),
    klad = create_boot_default_sequence(frame_num, cassette_handler, "Klad"),
    kurier = create_boot_default_sequence(frame_num, cassette_handler, "Kurier"),
    ladderovl = create_boot_default_sequence(frame_num, cassette_handler, "ladder.ovl"),
    ladder = create_boot_default_sequence(frame_num, cassette_handler, "ladder"),
    lrunnergms = create_boot_default_sequence(frame_num, cassette_handler, "LRUNNER.GMS"),
    lrunner = create_boot_default_sequence(frame_num, cassette_handler, "LRUNNER"),
    othello = create_boot_default_sequence(frame_num, cassette_handler, "OTHELLO"),
    otl9 = create_boot_default_sequence(frame_num, cassette_handler, "otl9"),
    p10k = create_boot_default_sequence(frame_num, cassette_handler, "p10k"),
    pacman = create_boot_default_sequence(frame_num, cassette_handler, "PACMAN"),
    perevoro = create_boot_default_sequence(frame_num, cassette_handler, "PEREVOROT"),
    popo = create_boot_default_sequence(frame_num, cassette_handler, "POPO"),
    raceovl = create_boot_default_sequence(frame_num, cassette_handler, "RACE.OVL"),
    race = create_boot_default_sequence(frame_num, cassette_handler, "RACE"),
    rever1 = create_boot_default_sequence(frame_num, cassette_handler, "Rever1"),
    rever2 = create_boot_default_sequence(frame_num, cassette_handler, "Rever2"),
    rotate = create_boot_default_sequence(frame_num, cassette_handler, "ROTATE"),
    rtype = create_boot_default_sequence(frame_num, cassette_handler, "RTYPE"),
    rtype1 = create_boot_default_sequence(frame_num, cassette_handler, "RTYPE1.LAB"),
    rtype2 = create_boot_default_sequence(frame_num, cassette_handler, "RTYPE2.LAB"),
    sokoban = create_boot_default_sequence(frame_num, cassette_handler, "SOKOBAN"),
    stalker = create_boot_default_sequence(frame_num, cassette_handler, "Stalker"),
    tetr3 = create_boot_default_sequence(frame_num, cassette_handler, "TETR3"),
    tetris = create_boot_default_sequence(frame_num, cassette_handler, "TETRIS"),
    tetro = create_boot_default_sequence(frame_num, cassette_handler, "Tetro"),
    xonix1 = create_boot_default_sequence(frame_num, cassette_handler, "XONIX1"),
    xonix5 = create_boot_default_sequence(frame_num, cassette_handler, "XONIX5"),
    zoom = create_boot_default_sequence(frame_num, cassette_handler, "ZOOM"),
}

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

    --- DEBUG: Print current frame number every 100 frames ---
    common_autoboot.debug_frame_num(frame_num)

    -- Execute the relevant boot sequence based on the loaded software
    local boot_function = boot_sequences[current_software_name]

    if not boot_function then -- If specific function not found
        boot_function = boot_sequences["default"] -- Assign the default function
    end

    if boot_function then
        boot_function(frame_num, cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)