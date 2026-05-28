-- jupace_cass.lua

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

-- --- Map all buttons ---
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
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

-- local function boot_default(title_to_type)
--     return function() 
--         common_autoboot.type_at_frame(frame_num, title_to_type .. "\n", 100)
--     end
-- end

local function boot_default(title_to_type) 
    return function(cassette_handler_arg)
        common_autoboot.type_at_frame(frame_num, title_to_type .. "\n", 100)

        common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 300)
        local cassette_load_done = cassette_handler_arg(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

        if cassette_load_done then
            -- emu.keypost('/\n')
        end
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(CASSETTE_SLOT).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    ['3dmaze'] = boot_default("load 3dmaze 3dmaze"),
    ['avoider'] = boot_default("load avoider run"),
    ['acecase'] = boot_default("load case"),
    ['demotape'] = boot_default("load banner"),
    ['graphics'] = boot_default("load ?plot"),
    ['graphicsa'] = boot_default("load ?plot"),
    ['aceinvad'] = boot_default("load graphics gr load run run"),
    ['invader1'] = boot_default("load GR load GR load GR load GM load GM load GM z p"),
    ['acemines'] = boot_default("load mines mines"),
    ['acestar'] = boot_default("0 0 bload astar 16384 call"),
    ['acevocab'] = boot_default("load listv"),
    ['acevader'] = boot_default("load gr load acevaders gr r"),
    ['adventa'] = boot_default("0 0 bload adva 16384 call"),
    ['aliendef'] = boot_default("load defender g"),
    ['aswarm'] = boot_default("load gr load swarm gr go"),
    ['amazmaze'] = boot_default("load maze g"),
    ['amisound'] = boot_default("load amisndkit go"),
    ['asmdasm'] = boot_default("load a1"),
    ['astrian'] = boot_default("load Lander run"),
    ['aticraid'] = boot_default("load atic go"),
    ['blackisl'] = boot_default("load black island"),
    ['bomber'] = boot_default("load bomber play"),
    ['breakout'] = boot_default("load breakout b"),
    ['calendar'] = boot_default("load calendar"),
    ['callisto'] = boot_default("8930 0 bload callisto"),
    ['cavern'] = boot_default("load graphics load run gr run"),
    ['cenipede'] = boot_default("load centipede go"),
    ['m_champs'] = boot_default("0 0 bload mines 11272 64 bload g load m 7 jeu"),
    ['chase'] = boot_default("load chase chase"),
    ['chess'] = boot_default("load chess run"),
    ['schess2'] = boot_default("load chess run"),
    ['cygnus'] = boot_default("load cygnus g"),
    ['database'] = boot_default("load database"),
    ['dodge'] = boot_default("load Dodger game"),
    ['dotman'] = boot_default("load s load run s run"),
    ['ducksht'] = boot_default("11272 0 bload dchars load duckshoot d"),
    ['firebird'] = boot_default("load FIREBIRD run"),
    ['frogger'] = boot_default("load frogger go"),
    ['frogger1'] = boot_default("load frogger g"),
    ['fungle'] = boot_default("load FU run"),
    ['gobbgook'] = boot_default("load gobblegook gobblegook"),
    ['grandprx'] = boot_default("load grandprix g"),
    ['grexfrog'] = boot_default("load graphics load run grf run"),
    ['guessing'] = boot_default("load game game"),
    ['hdrmon'] = boot_default("load HDRMON go"),
    ['invaders'] = boot_default("load invaders g"),
    ['jumpman'] = boot_default("load jumpman start"),
    ['kkong'] = boot_default("load CHARACTERS CHARACTERS load KONG run"),
    ['life'] = boot_default("load life13 life"),
    ['lightrac'] = boot_default("load LightRacer run"),
    ['loader'] = boot_default("load loader"),
    ['llander'] = boot_default("load ll ll"),
    ['memstars'] = boot_default("load run run"),
    ['meteor'] = boot_default("load gr meteor load meteor game"),
    ['metracer'] = boot_default("load GR load GR load GR load GM load GM z p"),
    ['meteors'] = boot_default("load asteroids g"),
    ['micromaz'] = boot_default("load graphics load run s run"),
    ['minefld'] = boot_default("11272 0 bload mchars load minefield m"),
    ['moonbugg'] = boot_default("load moonbuggy g"),
    ['morsecod'] = boot_default("load morse_tuto go"),
    ['othello'] = boot_default("load othello 11272 0 bload pieces go"),
    ['owler'] = boot_default("load owler loading"),
    ['quickdrw'] = boot_default("load quick-draw go"),
    ['quickdrp'] = boot_default("load Qdraw run"),
    ['robohnch'] = boot_default("load robohench g"),
    ['robohunt'] = boot_default("load robohunt g"),
    ['sailhorn'] = boot_default("load hornpipe hornpipe"),
    ['sambombs'] = boot_default("load sam g"),
    ['scramblr'] = boot_default("load scrambler"),
    ['sokoace'] = boot_default("load sokoace play"),
    ['sacemap'] = boot_default("load sokoed ed"),
    ['sbattle'] = boot_default("load graphics load run gr run"),
    ['spreadsh'] = boot_default("load s"),
    ['startrek'] = boot_default("load startrek g"),
    ['sudoku'] = boot_default("load sudoku sudoku"),
    ['surround'] = boot_default("load surround go"),
    ['tankbatl'] = boot_default("load tankbattle g"),
    ['teach'] = boot_default("load forth"),
    ['tetris'] = boot_default("load tetris tetris"),
    ['turbo'] = boot_default("load turbo 0 0 bload track turbo"),
    ['hanoi'] = boot_default("load hanoi hanoi"),
    ['words'] = boot_default("load words"),
    ['wrd'] = boot_default("load wrd"),
    ['zapem'] = boot_default("11272 0 bload zchars load zapem z"),
    ['zombies'] = boot_default("load zombpot zombpot"),
    ['zxprint'] = boot_default("load zx-printer"),
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
        boot_function(cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)