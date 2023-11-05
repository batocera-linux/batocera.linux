local lib = {}

local function get_settings_path()
	return emu.subst_env(manager.machine.options.entries.homepath:value():match('([^;]+)')) .. '/gunlight'	
end

local function get_settings_filename()
	return emu.romname() .. '.cfg'
end

local function initialize_button(settings)	
	local action = settings[1]	
	if action[2].port and action[3].mask and action[4].type and settings[3].key then
		local ioport = manager.machine.ioport								
		local offscreen_action = settings[2]
		if offscreen_action[2].port_offset == "n/a" then offscreen_action[2].port_offset = nil end									
		if offscreen_action[3].mask_offset == "n/a" then offscreen_action[3].mask_offset = nil end									
		if offscreen_action[4].type_offset == "n/a" then offscreen_action[4].type_offset = nil end									
		local new_button = {			
			port = action[2].port,
			mask = action[3].mask,
			type = ioport:token_to_input_type(action[4].type),			
			port_offset = offscreen_action[2].port_offset,
			mask_offset = offscreen_action[3].mask_offset,						
			type_offset = (offscreen_action[4].type_offset and ioport:token_to_input_type(offscreen_action[4].type_offset) or nil),
			key = manager.machine.input:seq_from_tokens(settings[3].key),
			key_cfg = settings[3].key,						
			input_delay = settings[4].input_delay,	
			flash_length = settings[5].flash_length,	
			brightness_gain = settings[6].brightness_gain,
			contrast_gain = settings[7].contrast_gain,
			gamma_gain = settings[8].gamma_gain,			
			counter = 0
		}		
		local port = ioport.ports[action[2].port]
		if port then
			local field = port:field(action[3].mask)
			if field and (field.type == new_button.type) then
				new_button.button = field
			end
		end
		local port_offset = (offscreen_action[2].port_offset and ioport.ports[offscreen_action[2].port_offset] or nil)
		if port_offset then
			local field_offset = port:field(offscreen_action[3].mask_offset)
			if field_offset and (field_offset.type == new_button.type_offset) then
				new_button.button_offset = field_offset
			end
		end
		return new_button
	end
	return nil
end

local function serialize_settings(button_list)
	local settings = {}
	for index, button in ipairs(button_list) do				
		local setting = {}
		local action = {}			
		local offscreen_action = {}
		table.insert(action, {button = 'Action'})				
		table.insert(action, {port = button.port})
		table.insert(action, {mask = button.mask})
		table.insert(action, {type = manager.machine.ioport:input_type_to_token(button.type)})
		table.insert(setting, action)	
		table.insert(offscreen_action, {button = 'Offscreen_Action'})				
		if (button.port_offset and button.mask_offset and button.type_offset) then						
			table.insert(offscreen_action, {port_offset = button.port_offset})
			table.insert(offscreen_action, {mask_offset = button.mask_offset})		
			table.insert(offscreen_action, {type_offset = manager.machine.ioport:input_type_to_token(button.type_offset)})	
		else
			table.insert(offscreen_action, {port_offset = "n/a"})
			table.insert(offscreen_action, {mask_offset = "n/a"})		
			table.insert(offscreen_action, {type_offset = "n/a"})	
		end	
		table.insert(setting,offscreen_action)
		table.insert(setting, {key = button.key_cfg})		
		table.insert(setting, {input_delay = button.input_delay})
		table.insert(setting, {flash_length = button.flash_length})
		table.insert(setting, {brightness_gain = button.brightness_gain})
		table.insert(setting, {contrast_gain = button.contrast_gain})
		table.insert(setting, {gamma_gain = button.gamma_gain})		
		table.insert(settings, setting)		
	end
	return settings
end

function lib:load_settings()
	local buttons = {}
	local json = require('json')
	local filename = get_settings_path() .. '/' .. get_settings_filename()
	local file = io.open(filename, 'r')
	if not file then
		return buttons
	end
	local loaded_settings = json.parse(file:read('a'))
	file:close()
	if not loaded_settings then
		emu.print_error(string.format('Error loading gunlight settings: error parsing file "%s" as JSON', filename))
		return buttons
	end
	for index, button_settings in ipairs(loaded_settings) do
		local new_button = initialize_button(button_settings)
		if new_button then
			buttons[#buttons + 1] = new_button
		end
	end
	return buttons
end

function lib:save_settings(buttons)
	local path = get_settings_path()
	local attr = lfs.attributes(path)
	if not attr then
		lfs.mkdir(path)
	elseif attr.mode ~= 'directory' then
		emu.print_error(string.format('Error saving gunlight settings: "%s" is not a directory', path))
		return
	end
	local filename = path .. '/' .. get_settings_filename()
	if #buttons == 0 then
		os.remove(filename)
		return
	end
	local json = require('json')
	local settings = serialize_settings(buttons)		
	local data = json.stringify(settings, {indent = true})	
	local file = io.open(filename, 'w')
	if not file then
		emu.print_error(string.format('Error saving gunlight settings: error opening file "%s" for writing', filename))
		return
	end
	file:write(data)
	file:close()
end

return lib
