local lib = {}

-- Common UI helper library
local commonui

-- Set of all menus
local MENU_TYPES = { MAIN = 0, EDIT = 1, ADD = 2, BUTTON = 3, BUTTON_OFFSET = 4 }

-- Set of sections within a menu
local MENU_SECTIONS = { HEADER = 0, CONTENT = 1, FOOTER = 2 }

-- Last index of header items (above main content) in menu
local header_height = 0

-- Last index of content items (below header, above footer) in menu
local content_height = 0

-- Stack of menus (see MENU_TYPES)
local menu_stack = { MENU_TYPES.MAIN }

-- Button to select when showing the main menu (so newly added button can be selected)
local initial_button

-- Saved selection on main menu (to restore after configure menu is dismissed)
local main_selection_save

-- Whether configure menu is active (so first item can be selected initially)
local configure_menu_active = false

-- Saved selection on configure menu (to restore after button menu is dismissed)
local configure_selection_save

-- Helper for polling for hotkeys
local hotkey_poller

-- Button being created/edited
local current_button = {}

-- Initial button to select when opening buttons menu
local initial_input

-- Initial button to select when opening buttons offset menu
local initial_input_offset

-- Handler for BUTTON menu
local input_menu

-- Handler for BUTTON OFFSET menu
local input_menu_offset


-- Returns the section (from MENU_SECTIONS) and the index within that section
local function menu_section(index)
	if index <= header_height then
		return MENU_SECTIONS.HEADER, index
	elseif index <= content_height then
		return MENU_SECTIONS.CONTENT, index - header_height
	else
		return MENU_SECTIONS.FOOTER, index - content_height
	end
end

local function create_new_button()
	return {
		port_offset = nil,
		mask_offset = nil,
		type_offset = nil,	        		
		input_delay = 0,
		flash_length = -1,				
		brightness_gain = 0.5,
		contrast_gain = 0.0,
		gamma_gain = 0.0,		
		counter = 0
	}
end

local function is_button_complete(button)
	return button.port and button.mask and button.type and button.key and button.button and button.counter 
end

-- Main menu

local function populate_main_menu(buttons)
	local ioport = manager.machine.ioport
	local input = manager.machine.input
	local menu = {}
	table.insert(menu, {_p('plugin-gunlight', 'Gunlight buttons'), '', 'off'})
	table.insert(menu, {string.format(_p('plugin-gunlight', 'Press %s to delete'), manager.ui:get_general_input_setting(ioport:token_to_input_type('UI_CLEAR'))), '', 'off'})
	table.insert(menu, {'---', '', ''})
	header_height = #menu

	-- Use frame rate of first screen or 60Hz if no screens
	local freq = 60
	local screen = manager.machine.screens:at(1)
	if screen then
		freq = 1 / screen.frame_period
	end

	if #buttons > 0 then
		for index, button in ipairs(buttons) do
			-- Round rate to two decimal places
			local rate = freq / 1
			rate = math.floor(rate * 100) / 100
			local text
			if button.button then
				if button.button_offset then
					text = string.format(_p('plugin-gunlight', '%s [%s]'), button.button.name .. '/' .. button.button_offset.name, "offset")
				else
					text = string.format(_p('plugin-gunlight', '%s'), button.button.name)
				end	
			else
				text = string.format(_p('plugin-gunlight', 'n/a'))
			end
			table.insert(menu, {text, input:seq_name(button.key), ''})
			if index == initial_button then
				main_selection_save = #menu
			end
		end
	else
		table.insert(menu, {_p('plugin-gunlight', '[no gunlight buttons]'), '', 'off'})
	end
	initial_button = nil
	content_height = #menu

	table.insert(menu, {'---', '', ''})
	table.insert(menu, {_p('plugin-gunlight', 'Add gunlight button'), '', ''})

	local selection = main_selection_save
	main_selection_save = nil
	return menu, selection
end

local function handle_main_menu(index, event, buttons)
	local section, adjusted_index = menu_section(index)
	if section == MENU_SECTIONS.CONTENT then
		if event == 'select' then
			main_selection_save = index
			current_button = buttons[adjusted_index]
			table.insert(menu_stack, MENU_TYPES.EDIT)
			return true
		elseif event == 'clear' then
			table.remove(buttons, adjusted_index)
			main_selection_save = index
			if adjusted_index > #buttons then
				main_selection_save = main_selection_save - 1
			end
			return true
		end
	elseif section == MENU_SECTIONS.FOOTER then
		if event == 'select' then
			main_selection_save = index
			current_button = create_new_button()
			table.insert(menu_stack, MENU_TYPES.ADD)
			return true
		end
	end
	return false
end

-- Add/edit menus (mostly identical)

local function populate_configure_menu(menu)
	local button_name
	
	if current_button.button then
		button_name = current_button.button.name
	elseif current_button.port then
		button_name = _p('plugin-gunlight', 'n/a')
	else
		button_name = _p('plugin-gunlight', '[not set]')
	end
	
	table.insert(menu, {_p('plugin-gunlight', 'Action'), button_name, ''})
	if not (configure_menu_active or configure_selection_save) then
		configure_selection_save = #menu
	end
	
	local button_name_offset
	if current_button.button_offset then
		button_name_offset = current_button.button_offset.name
	elseif current_button.port_offset then
		button_name_offset = _p('plugin-gunlight', 'n/a')
	else
		button_name_offset = _p('plugin-gunlight', '[not set]')
	end
	
	table.insert(menu, {_p('plugin-gunlight', 'Offscreen Action'), button_name_offset, ''})
	
	local key_name = current_button.key and manager.machine.input:seq_name(current_button.key) or _p('plugin-gunlight', '[not set]')
	table.insert(menu, {_p('plugin-gunlight', 'Input'), key_name, hotkey_poller and 'lr' or ''})
		
	table.insert(menu, {_p('plugin-gunlight', 'Input Delay'), current_button.input_delay, current_button.input_delay > 0 and 'lr' or 'r'})
	table.insert(menu, {_p('plugin-gunlight', 'Flash Length'), current_button.flash_length, current_button.flash_length > -1 and 'lr' or 'r'})		
		
	table.insert(menu, {_p('plugin-gunlight', 'Flash Brightness'), current_button.brightness_gain, current_button.brightness_gain > 0 and 'lr' or 'r'})
	table.insert(menu, {_p('plugin-gunlight', 'Flash Contrast'), current_button.contrast_gain, current_button.contrast_gain > 0 and 'lr' or 'r'})
	table.insert(menu, {_p('plugin-gunlight', 'Flash Gamma'), current_button.gamma_gain, current_button.gamma_gain > 0 and 'lr' or 'r'})	
	
	configure_menu_active = true
end

local function handle_configure_menu(index, event)
	if hotkey_poller then
		-- special handling for polling for hotkey
		if hotkey_poller:poll() then
			if hotkey_poller.sequence then
				current_button.key = hotkey_poller.sequence
				current_button.key_cfg = manager.machine.input:seq_to_tokens(hotkey_poller.sequence)
			end
			hotkey_poller = nil
			return true
		end
		return false
	end

	if index == 1 then
		-- Action
		if event == 'select' then
			configure_selection_save = header_height + index
			table.insert(menu_stack, MENU_TYPES.BUTTON)
			if current_button.port and current_button.button then
				initial_input = current_button.button
			end
			return true
		end
	elseif index == 2 then
		--  Offscreen Action
		if event == 'select' then
			configure_selection_save = header_height + index
			table.insert(menu_stack, MENU_TYPES.BUTTON_OFFSET)
			if current_button.port_offset and current_button.button_offset then
				initial_input_offset = current_button.button_offset
			end
			return true
		end
	elseif index == 3 then
		-- Hotkey
		if event == 'select' then
			if not commonui then
				commonui = require('commonui')
			end
			hotkey_poller = commonui.switch_polling_helper()
			return true
		end			
	elseif index == 4 then
		-- Input delay
		manager.machine:popmessage(_p('plugin-gunlight', 'Input Delay'))
		if event == 'left' then
			current_button.input_delay = current_button.input_delay - 1			
			return true
		elseif event == 'right' then
			current_button.input_delay = current_button.input_delay + 1
			return true
		elseif event == 'clear' then
			current_button.input_delay = 1
			return true
		end
	elseif index == 5 then
		-- Flash length
		manager.machine:popmessage(_p('plugin-gunlight', 'Flash Length (set -1 for until release)'))
		if event == 'left' then
			current_button.flash_length = current_button.flash_length - 1
			if current_button.flash_length < -1 then
			 current_button.flash_length = -1
			end 
			return true
		elseif event == 'right' then
			current_button.flash_length = current_button.flash_length + 1
			return true
		elseif event == 'clear' then
			current_button.flash_length = 1
			return true
		end			
	elseif index == 6 then
		-- Brightness gain
		manager.machine:popmessage(_p('plugin-gunlight', 'Brightness gain for gun button'))
		if event == 'left' then
			current_button.brightness_gain = current_button.brightness_gain - 0.1
			if current_button.brightness_gain < 0.01 then
			 current_button.brightness_gain = 0
			end 
			return true
		elseif event == 'right' then
			current_button.brightness_gain = current_button.brightness_gain + 0.1
			if current_button.brightness_gain > 1 then
			 current_button.brightness_gain = 1
			end 
			return true
		elseif event == 'clear' then
			current_button.brightness_gain = 0.5
			return true
		end
	elseif index == 7 then
		-- Contrast gain
		manager.machine:popmessage(_p('plugin-gunlight', 'Contrast gain for gun button'))
		if event == 'left' then
			current_button.contrast_gain = current_button.contrast_gain - 0.1
			if current_button.contrast_gain < 0.01 then
			 current_button.contrast_gain = 0
			end 
			return true
		elseif event == 'right' then
			current_button.contrast_gain = current_button.contrast_gain + 0.1
			if current_button.contrast_gain > 1 then
			 current_button.contrast_gain = 1
			end 
			return true
		elseif event == 'clear' then
			current_button.contrast_gain = 0.5
			return true
		end	
	elseif index == 8 then
		-- Gamma gain
		manager.machine:popmessage(_p('plugin-gunlight', 'Gamma gain for gun button'))
		if event == 'left' then
			current_button.gamma_gain = current_button.gamma_gain - 0.1
			if current_button.gamma_gain < 0.01 then
			 current_button.gamma_gain = 0
			end 
			return true
		elseif event == 'right' then
			current_button.gamma_gain = current_button.gamma_gain + 0.1
			if current_button.gamma_gain > 2 then
			 current_button.gamma_gain = 2
			end 
			return true
		elseif event == 'clear' then
			current_button.gamma_gain = 0.5
			return true
		end				
	end
	return false
end

local function populate_edit_menu()
	local menu = {}
	table.insert(menu, {_p('plugin-gunlight', 'Edit gunlight button'), '', 'off'})
	table.insert(menu, {'---', '', ''})
	header_height = #menu

	populate_configure_menu(menu)
	content_height = #menu

	table.insert(menu, {'---', '', ''})
	table.insert(menu, {_p('plugin-gunlight', 'Done'), '', ''})

	local selection = configure_selection_save
	configure_selection_save = nil
	if hotkey_poller then
		return hotkey_poller:overlay(menu, selection, 'lrrepeat')
	else
		return menu, selection, 'lrrepeat'
	end
end

local function handle_edit_menu(index, event, buttons)
	local section, adjusted_index = menu_section(index)
	if ((section == MENU_SECTIONS.FOOTER) and (event == 'select')) or (event == 'cancel') then
		configure_menu_active = false
		table.remove(menu_stack)
		return true
	elseif section == MENU_SECTIONS.CONTENT then
		return handle_configure_menu(adjusted_index, event)
	end
	return false
end

local function populate_add_menu()
	local menu = {}
	table.insert(menu, {_p('plugin-gunlight', 'Add gunlight button'), '', 'off'})
	table.insert(menu, {'---', '', ''})
	header_height = #menu

	populate_configure_menu(menu)
	content_height = #menu

	table.insert(menu, {'---', '', ''})
	if is_button_complete(current_button) then
		table.insert(menu, {_p('plugin-gunlight', 'Create'), '', ''})
	else
		table.insert(menu, {_p('plugin-gunlight', 'Cancel'), '', ''})
	end

	local selection = configure_selection_save
	configure_selection_save = nil
	if hotkey_poller then
		return hotkey_poller:overlay(menu, selection, 'lrrepeat')
	else
		return menu, selection, 'lrrepeat'
	end
end

local function handle_add_menu(index, event, buttons)
	local section, adjusted_index = menu_section(index)
	if ((section == MENU_SECTIONS.FOOTER) and (event == 'select')) or (event == 'cancel') then
		configure_menu_active = false
		table.remove(menu_stack)
		if is_button_complete(current_button) and (event == 'select') then
			table.insert(buttons, current_button)
			initial_button = #buttons
		end
		return true
	elseif section == MENU_SECTIONS.CONTENT then
		return handle_configure_menu(adjusted_index, event)
	end
	return false
end

-- Button selection menu

local function populate_button_menu()
	local function is_supported_input(ioport_field)
		-- IPT_BUTTON1 through IPT_BUTTON16 in ioport_type enum (ioport.h)
		return ioport_field.type >= 64 and ioport_field.type <= 79
	end

	local function action(field)
		if field then
			current_button.port = field.port.tag						
			current_button.mask = field.mask
			current_button.type = field.type
			current_button.button = field			
		end
		initial_input = nil
		input_menu = nil
		table.remove(menu_stack)
	end

	if not commonui then
		commonui = require('commonui')
	end
	input_menu = commonui.input_selection_menu(action, _p('plugin-gunlight', 'Select an Action'), is_supported_input)
	return input_menu:populate(initial_input)
end

-- Button offset selection menu

local function populate_button_offset_menu()
	local function is_supported_input_offset(ioport_field)
		-- IPT_BUTTON1 through IPT_BUTTON16 in ioport_type enum (ioport.h)
		return ioport_field.type >= 64 and ioport_field.type <= 79
	end

	local function action_offset(field)
		if field then
			current_button.port_offset = field.port.tag						
			current_button.mask_offset = field.mask
			current_button.type_offset = field.type
			current_button.button_offset = field			
		end
		initial_input_offset = nil
		input_menu_offset = nil
		table.remove(menu_stack)
	end

	if not commonui then
		commonui = require('commonui')
	end
	input_menu_offset = commonui.input_selection_menu(action_offset, _p('plugin-gunlight', 'Select an Offset Action'), is_supported_input_offset)
	return input_menu_offset:populate(initial_input_offset)
end

local function handle_button_menu(index, event)
	return input_menu:handle(index, event)
end

local function handle_button_offset_menu(index, event)
	return input_menu_offset:handle(index, event)
end

function lib:init_menu(buttons)
	header_height = 0
	content_height = 0
	menu_stack = { MENU_TYPES.MAIN }
	current_button = {}
	input_menu = nil
	input_menu_offset = nil
end

function lib:populate_menu(buttons)
	local current_menu = menu_stack[#menu_stack]
	if current_menu == MENU_TYPES.MAIN then
		return populate_main_menu(buttons)
	elseif current_menu == MENU_TYPES.EDIT then
		return populate_edit_menu()
	elseif current_menu == MENU_TYPES.ADD then
		return populate_add_menu()
	elseif current_menu == MENU_TYPES.BUTTON then
		return populate_button_menu()
	elseif current_menu == MENU_TYPES.BUTTON_OFFSET then
		return populate_button_offset_menu()	
	end
end

function lib:handle_menu_event(index, event, buttons)
	manager.machine:popmessage()
	local current_menu = menu_stack[#menu_stack]
	if current_menu == MENU_TYPES.MAIN then
		return handle_main_menu(index, event, buttons)
	elseif current_menu == MENU_TYPES.EDIT then
		return handle_edit_menu(index, event, buttons)
	elseif current_menu == MENU_TYPES.ADD then
		return handle_add_menu(index, event, buttons)
	elseif current_menu == MENU_TYPES.BUTTON then
		return handle_button_menu(index, event)
	elseif current_menu == MENU_TYPES.BUTTON_OFFSET then
		return handle_button_offset_menu(index, event)	
	end
end

return lib
