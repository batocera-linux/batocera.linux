local exports = {}
exports.name = 'coindrop'
exports.version = '1'
exports.description = 'Coin drop sounds'
exports.license = 'GPL'
exports.author = { name = 'Ian Murray' }

-- Assistance provided by cuavas on Reddit with optimizing the original version
-- Sound player code from DKChorus plugin by Jon Wilson (10yard)
-- External sounds on Windows systems using "sounder" by Eli Fulkerston:
-- https://download.elifulkerson.com/files/sounder/
-- For future expansion: add sounds for different coin levels, use coinCount to select.

local coindrop = exports
function coindrop.startplugin()
	local coinPorts = {}
	local coinCount = nil
	local portman = nil
	local useaplay = nil
	local pluginFolder = nil

	local function get_plugin_path()
		return emu.subst_env(manager.machine.options.entries.pluginspath:value():match('([^;]+)')) .. '/coindrop'
	end

	local function process_frame()
		-- Check input for coin port activity
		for i, port in pairs(coinPorts) do
            local val = port[1]:read()
            for j, field in pairs(port[2]) do
                local active = (val & field[1].mask) ~= field[1].defvalue
                if active then
                    if not field[2] then
                    	coinCount = coinCount + 1
                        emu.print_verbose(string.format('CoinDrop: %s pressed, %d total coins inserted', field[1].name, coinCount))
                        playCoinSound()
                    end
                end
                field[2] = active
            end
        end
    end

	local function cleanup()
		portman = nil
		coinCount = nil
		useaplay = nil
		pluginFolder = nil
		coinPorts = {}
		emu.register_frame(nil)
	end

	function is_linux()
		return package.config:sub(1,1) == "/"
	end

	local function init_plugin()
		math.randomseed(os.time())
		math.random(); math.random(); math.random()
		coinCount = 0
		useaplay = is_linux()
		pluginFolder = get_plugin_path()

		-- Play a short silent sound to initialize the sound system,
		-- otherwise, there will be a lag when the first coin is inserted.
		emu.print_verbose('CoinDrop: Initialize sound playback')
		playSound("silent")

		-- Scan inputs, save ports named COIN[number]
		emu.print_verbose('CoinDrop: Checking inputs')
		portman = manager.machine.ioport
		for t, p in pairs(portman.ports) do
    		local fields = {}
    		for n, f in pairs(p.fields) do
        		if portman:input_type_to_token(f.type, f.player):match('^COIN[0-9]+$') then
        			emu.print_verbose(string.format('CoinDrop: Found coin input %s', portman:input_type_to_token(f.type, f.player)))
            		table.insert(fields, { f, false })
        		end
        	end
        	if #fields > 0 then
    			emu.print_verbose(string.format('CoinDrop: Saving coin input ports, total count: %d', #fields))
        		table.insert(coinPorts, { p, fields })
    		end
    	end
	end

	function playCoinSound()
		-- Select one of three random sounds to use
		local soundFile = nil
		soundChoice = math.random(1,3)
		if soundChoice == 1 then
			soundFile = "coin1"
		elseif soundChoice == 2 then
			soundFile = "coin2"
		else
			soundFile = "coin3"
		end
		playSound(soundFile)
	end

	function playSound(soundFile)
		-- Playback using aplay on Linux or Sounder on Windows
		local volume = 100
		if useaplay then
			emu.print_verbose(string.format("CoinDrop: Playing sound %s.wav using aplay", soundFile))
			io.popen("aplay -q "..pluginFolder.."/sounds/"..soundFile..".wav &")
		else
			emu.print_verbose(string.format("CoinDrop: Playing sound %s.wav using sounder", soundFile))
			io.popen("start "..pluginFolder.."/bin/sounder.exe /volume "..tostring(volume).." /id "..pluginFolder.."/sounds/"..soundFile..".wav /stopbyid "..soundFile.." plugins/coindrop/sounds/"..soundFile..".wav")
		end
	end

	emu.register_start(init_plugin)
	emu.register_frame(process_frame)
	emu.register_stop(cleanup)
end

return exports