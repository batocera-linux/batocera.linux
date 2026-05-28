-- super80_cass.lua

-- WIP: need to figure out how to load games with usage <info name="usage" value="LOAD while in BASIC, then RUN" />

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

common_autoboot.populate_buttons(button)

common_autoboot.print_image_info()

-- Print the button table contents for debugging
-- common_autoboot.print_buttons(button)

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function boot_default(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 100, BUTTON_PRESS_DURATION)

    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 400) -- need to wait at least 300 frames after CLOAD cmd, otherwise will have LOADING ERROR!

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if cassette_load_done then
        emu.keypost('RUN\n')
    end
end

local function create_boot_type_1_sequence(title_to_type) 
    return function(cassette_handler_arg)
        common_autoboot.type_at_frame(frame_num, "L\n", 100)
        common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 200)

        local cassette_load_done = cassette_handler_arg(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

        if cassette_load_done then
            emu.keypost(title_to_type .. '\n')
        end
    end
end

local function create_boot_type_2_sequence()
    return function(cassette_handler_arg)
        common_autoboot.type_at_frame(frame_num, "GD000\n", 100)  -- GD000 to enter BASIC MODE
        common_autoboot.type_at_frame(frame_num, "LOAD\n", 200)
        common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 300)

        local cassette_load_done = cassette_handler_arg(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

        if cassette_load_done then
            emu.keypost('RUN\n')
        end
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(3).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    aim = create_boot_type_2_sequence(),
    accounts = create_boot_type_2_sequence(),
    add = create_boot_type_2_sequence(),
    basic = create_boot_type_1_sequence("G100"),
    basic1 = create_boot_type_1_sequence("G100"),
    bio = create_boot_type_2_sequence(),
    bunny = create_boot_type_2_sequence(),
    camel = create_boot_type_2_sequence(),
    cap = create_boot_type_2_sequence(),
    carrace = create_boot_type_2_sequence(),
    cavemon = create_boot_type_2_sequence(),
    cavemon4 = create_boot_type_2_sequence(),
    cavepit = create_boot_type_2_sequence(),
    chase = create_boot_type_2_sequence(),
    chomp = create_boot_type_2_sequence(),
    chucka = create_boot_type_2_sequence(),
    crash = create_boot_type_2_sequence(),
    crashj = create_boot_type_2_sequence(),
    crazym = create_boot_type_1_sequence("G0"),
    crazymj = create_boot_type_1_sequence("G0"),
    crosfire = create_boot_type_2_sequence(),
    cvoicec = create_boot_type_2_sequence(),
    cvoicei = create_boot_type_2_sequence(),
    debug = create_boot_type_1_sequence("G100"),
    debug4 = create_boot_type_1_sequence("G100"),
    dungeon = create_boot_type_2_sequence(),
    dungeon4 = create_boot_type_2_sequence(),
    edasm = create_boot_type_1_sequence("G8000"),
    eldraw = create_boot_type_1_sequence("G100"),
    epromp = create_boot_type_2_sequence(),
    epromr = create_boot_type_2_sequence(),
    findword = create_boot_type_2_sequence(),
    hangman = create_boot_type_2_sequence(),
    horserac = create_boot_type_2_sequence(),
    horserace4 = create_boot_type_2_sequence(),
    horseracem = create_boot_type_2_sequence(),
    hydrax = create_boot_type_2_sequence(),
    hydraxj = create_boot_type_2_sequence(),
    inva = create_boot_type_1_sequence("G400"),
    inva1 = create_boot_type_1_sequence("G400"),
    inva1j = create_boot_type_1_sequence("G400"),
    inva2 = create_boot_type_1_sequence("G400"),
    inva2j = create_boot_type_1_sequence("G400"),
    invanal = create_boot_type_2_sequence(),
    juggle = create_boot_type_2_sequence(),
    lcxf = create_boot_type_2_sequence(),
    life = create_boot_type_1_sequence("G0"),
    loancalc = create_boot_type_2_sequence(),
    lunar1 = create_boot_type_2_sequence(),
    lunar2 = create_boot_type_2_sequence(),
    lunar3 = create_boot_type_2_sequence(),
    lwriter = create_boot_type_2_sequence(),
    lwriter4 = create_boot_type_2_sequence(),
    l2basic = create_boot_type_1_sequence("G0"),
    masterm = create_boot_type_2_sequence(),
    matchmat = create_boot_type_2_sequence(),
    maths = create_boot_type_2_sequence(),
    mem = create_boot_type_2_sequence(),
    meteor = create_boot_type_2_sequence(),
    meteorj = create_boot_type_2_sequence(),
    minitype = create_boot_type_1_sequence("G8000"),
    minit1 = create_boot_type_1_sequence("GB700"),
    minit3 = create_boot_type_1_sequence("G8000"),
    missile = create_boot_type_2_sequence(),
    missile4 = create_boot_type_2_sequence(),
    missile4j = create_boot_type_2_sequence(),
    moneytst = create_boot_type_2_sequence(),
    monopoly = create_boot_type_2_sequence(),
    moorads = create_boot_type_2_sequence(),
    morse = create_boot_type_2_sequence(),
    mortor1 = create_boot_type_2_sequence(),
    mortor2 = create_boot_type_2_sequence(),
    mortor4 = create_boot_type_2_sequence(),
    onearm = create_boot_type_2_sequence(),
    onearm4 = create_boot_type_2_sequence(),
    opposite = create_boot_type_2_sequence(),
    othello = create_boot_type_2_sequence(),
    pelatron = create_boot_type_1_sequence("G100"),
    petrol = create_boot_type_2_sequence(),
    pi = create_boot_type_2_sequence(),
    planet = create_boot_type_2_sequence(),
    pontoon = create_boot_type_2_sequence(),
    puzzle = create_boot_type_2_sequence(),
    riverboa = create_boot_type_2_sequence(),
    riverboatj = create_boot_type_2_sequence(),
    rotate = create_boot_type_2_sequence(),
    russroul = create_boot_type_2_sequence(),
    s80solit = create_boot_type_2_sequence(),
    sets = create_boot_type_2_sequence(),
    shell = create_boot_type_2_sequence(),
    shell4 = create_boot_type_2_sequence(),
    shootgal = create_boot_type_2_sequence(),
    shootgal1 = create_boot_type_2_sequence(),
    sinv = create_boot_type_2_sequence(),
    sinvj = create_boot_type_2_sequence(),
    skier = create_boot_type_2_sequence(),
    smart = create_boot_type_1_sequence("G100"),
    snake = create_boot_type_2_sequence(),
    snakej = create_boot_type_2_sequence(),
    solit = create_boot_type_2_sequence(),
    soundemo = create_boot_type_2_sequence(),
    stopwatc = create_boot_type_2_sequence(),
    suprtrek = create_boot_type_2_sequence(),
    sword = create_boot_type_2_sequence(),
    takeaway = create_boot_type_2_sequence(),
    tenpin = create_boot_type_2_sequence(),
    thisisbu = create_boot_type_2_sequence(),
    thisisbu4 = create_boot_type_2_sequence(),
    tibetian = create_boot_type_2_sequence(),
    tictac = create_boot_type_2_sequence(),
    treasure = create_boot_type_2_sequence(),
    vonshrin = create_boot_type_2_sequence(),
    x6845p = create_boot_type_2_sequence(),
    x4inarow = create_boot_type_2_sequence(),
    xaa = create_boot_type_1_sequence("G100"),
    xaaj = create_boot_type_1_sequence("G100"),
    xadvland = create_boot_type_1_sequence("G3DE0"),
    xaster = create_boot_type_1_sequence("G100"),
    xasterj = create_boot_type_1_sequence("G100"),
    xastp = create_boot_type_1_sequence("G349B"),
    xastp3 = create_boot_type_1_sequence("G349B"),
    xastp3j = create_boot_type_1_sequence("G349B"),
    xastro = create_boot_type_1_sequence("G100"),
    xastroj = create_boot_type_1_sequence("G100"),
    xatc = create_boot_type_1_sequence("G0"),
    xbemon = create_boot_type_1_sequence("G6000"),
    xbeez80 = create_boot_type_1_sequence("GA00"),
    xcdes = create_boot_type_1_sequence("G100"),
    xcstrek = create_boot_type_1_sequence("G100"),
    xcaliens = create_boot_type_1_sequence("G100"),
    xcharp = create_boot_type_2_sequence(),
    xchomp = create_boot_type_1_sequence("G100"),
    xchompj = create_boot_type_1_sequence("G100"),
    xcorral = create_boot_type_2_sequence(),
    xdemon = create_boot_type_1_sequence("G0"),
    xdefend = create_boot_type_1_sequence("G100"),
    xexmon = create_boot_type_1_sequence("GAA00"),
    xexmon3 = create_boot_type_1_sequence("GAA00"),
    xfgam = create_boot_type_1_sequence("G1F0"),
    xgalax2j = create_boot_type_1_sequence("G100"),
    xgalaxj = create_boot_type_1_sequence("G100"),
    xgrtkitf = create_boot_type_2_sequence(),
    xhangman = create_boot_type_2_sequence(),
    xhoh = create_boot_type_2_sequence(),
    xhoh3 = create_boot_type_2_sequence(),
    xkadath = create_boot_type_2_sequence(),
    xkilo = create_boot_type_1_sequence("G1C0A"),
    xkilo1 = create_boot_type_1_sequence("G1C0A"),
    xkilo1j = create_boot_type_1_sequence("G1C0A"),
    xkiloj = create_boot_type_1_sequence("G1C0A"),
    xmart = create_boot_type_1_sequence("G0"),
    xmart1j = create_boot_type_1_sequence("G0"),
    xmerlin = create_boot_type_2_sequence(),
    xmerlin2 = create_boot_type_2_sequence(),
    xmidas = create_boot_type_1_sequence("G200"),
    xmission = create_boot_type_1_sequence("G3C80"),
    xpenetr = create_boot_type_1_sequence("G100"),
    xpenetrj = create_boot_type_1_sequence("G100"),
    xpinegap = create_boot_type_2_sequence(),
    xschess1 = create_boot_type_1_sequence("G100"),
    xschess2 = create_boot_type_1_sequence("G4040"),
    xsupinv = create_boot_type_2_sequence(),
    xsupinvj = create_boot_type_2_sequence(),
    xvalley = create_boot_type_2_sequence(),
    xvalley3 = create_boot_type_2_sequence(),
    xvalley3a = create_boot_type_2_sequence(),
    xwbee = create_boot_type_1_sequence("G9000"),
    xwbee2 = create_boot_type_1_sequence("G9000"),
    xbreak = create_boot_type_2_sequence(),
    xbreakj = create_boot_type_2_sequence(),
    xmsinv = create_boot_type_1_sequence("G1000"),
    xmsinvj = create_boot_type_1_sequence("G1000"),
    xmsinv2 = create_boot_type_1_sequence("G1000"),
    xmsinv2j = create_boot_type_1_sequence("G1000"),
    xsub = create_boot_type_2_sequence(),
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
    end

    -- --- Print current frame number every 100 frames ---
    -- if frame_num % 100 == 0 then -- The modulo operator (%) gives the remainder of a division
    --     emu.print_info("Current Frame: " .. frame_num)
    -- end    

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