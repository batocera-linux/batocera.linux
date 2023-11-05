-- license:BSD-3-Clause
-- copyright-holders:Jack Li
local exports = {
	name = 'gunlight',
	version = '0.0.5',
	description = 'Gunlight plugin',
	license = 'BSD-3-Clause',
	author = { name = 'Jack Li / Psakhis' } }

table.maxn = table.maxn or function(t) return #t end

local gunlight = exports

local machine_screen = nil
local user_set_brightness = nil
local user_set_contrast = nil
local user_set_gamma = nil
local gain_set_brightness = 0.0
local gain_set_contrast = 0.0
local gain_set_gamma = 0.0
local num_frames_gain = 0
local gain_applied = false
local lag_stack = {}
local lag_key = {}

function gunlight.startplugin()

	-- List of gunlight buttons, each being a table with keys:
	--   'port' - port name of the button 
	--   'mask' - mask of the button field 
	--   'type' - input type of the button 
	--   'port_offset' - port name of the button if offset
	--   'mask_offset' - mask of the button field if offset
	--   'type_offset' - input type of the button if offset
	--   'key' - input_seq of the keybinding
	--   'key_cfg' - configuration string for the keybinding
	--   'input_delay' - lag of frames to apply key
	--   'flash_length' - number of frames of gain 
	--   'brightness_gain' - increase brightness for gun button
	--   'contrast_gain' - increase contrast for gun button
	--   'gamma_gain' - increase gamma for gun button	
	--   'button' - reference to ioport_field
	--   'button_offset' - reference to ioport_field for offset
	--   'counter' - position in key cycle
	local buttons = {}

	local menu_handler
        
        local function save_user_settings()
                local user_set = manager.machine.screens[machine_screen].container.user_settings                    	        	
		user_set_brightness = user_set.brightness 
	        user_set_contrast = user_set.contrast
	        user_set_gamma = user_set.gamma	        	        
        end
        
        local function restore_user_settings()
         	--local COLOR_WHITE = 0xffffffff
		--manager.machine.screens[":screen"]:draw_box(0, 0,  manager.machine.screens[":screen"].width, manager.machine.screens[":screen"].height, COLOR_WHITE,COLOR_WHITE)
		
        	if gain_applied then         	
	        	local user_set = manager.machine.screens[machine_screen].container.user_settings	        	
	        	user_set.brightness = user_set_brightness 
	        	user_set.contrast = user_set_contrast 
	        	user_set.gamma = user_set_gamma
	               	manager.machine.screens[machine_screen].container.user_settings = user_set
	               	gain_applied = false
	               	gain_set_brightness = 0.0
	        	gain_set_contrast = 0.0
	        	gain_set_gamma = 0.0		        		        	        	
	        end	
        end
        
        local function restore_gain_settings()
        	local user_set = manager.machine.screens[machine_screen].container.user_settings        	
		user_set.brightness = user_set_brightness + gain_set_brightness 
	        user_set.contrast = user_set_contrast + gain_set_contrast
	        user_set.gamma = user_set_gamma + gain_set_gamma
	        manager.machine.screens[machine_screen].container.user_settings = user_set
	        gain_applied = true		                       	      
        end
        
        local function guncode_offset(key_cfg)        
        	local guncode_key_x = "GUNCODE_1_XAXIS"
        	local guncode_key_y = "GUNCODE_1_YAXIS"  
        	local guncode_xaxis = nil
        	local guncode_yaxis = nil   	                	
        	--emu.print_verbose("key_cfg ".. key_cfg)            			
		local _, j = string.find(key_cfg, "GUNCODE_")
		if j then
			local guncode_n = string.sub(key_cfg,j+1,j+1)
			guncode_key_x = "GUNCODE_" .. guncode_n .. "_XAXIS"
			guncode_key_y = "GUNCODE_" .. guncode_n .. "_YAXIS"
		end
		guncode_xaxis = manager.machine.input:code_from_token(guncode_key_x)	
		guncode_yaxis = manager.machine.input:code_from_token(guncode_key_y)								
		local guncode_x = manager.machine.input:code_value(guncode_xaxis)
	 	local guncode_y = manager.machine.input:code_value(guncode_yaxis)		 	
		--emu.print_verbose("guncode X " .. guncode_x)
		--emu.print_verbose("guncode Y " .. guncode_y)
		if (guncode_x == -65536 and guncode_y == -65536) then					       				
			return 1
		else						       
			return 0
		end		
        end
               
	local function process_frame()
		local input = manager.machine.input						
					
		local function process_button(button)
			local pressed = input:seq_pressed(button.key)							
			--local player = manager.machine.ioport.ports[button.port]:field(button.mask).player
			
			if pressed then							
				button.counter = button.counter + 1	
				
				if button.flash_length == -1 then
					if num_frames_gain <= 0 then
						num_frames_gain = 1 
					end	
				else
					--if button.counter == 1 and not gain_applied then
					if button.counter == 1 then
						if num_frames_gain < button.flash_length then
							num_frames_gain = button.flash_length 
						end							
					end							
				end		
																																													   				
				if  button.brightness_gain > gain_set_brightness then
					gain_set_brightness = button.brightness_gain
				end									
				if  button.contrast_gain > gain_set_contrast then
					gain_set_contrast = button.contrast_gain
				end									
				if  button.gamma_gain > gain_set_gamma then
					gain_set_gamma = button.gamma_gain
				end
																			
				table.insert(lag_stack,button.input_delay)
				table.insert(lag_key,button.port .. '\0' .. button.mask .. '.' .. button.type)			
				return 1			        				
			else						        
				button.counter = 0											
				return 0
			end
		end
                                                
		-- Initialize buttons
		local button_states = {} 			  		                          	               		
		for i, button in ipairs(buttons) do
			if button.button then			        
				local key = button.port .. '\0' .. button.mask .. '.' .. button.type									
				local state = {0, button}
				process_button(button)									
				button_states[key] = state														
			end
		end						 			 								
		
		-- Apply flash gain	
		--emu.print_verbose("gain " .. num_frames_gain)	
		if num_frames_gain <= 0 then
			if gain_applied then
				restore_user_settings()
			end
		else				
			if not gain_applied then
				save_user_settings()
				restore_gain_settings()			
			end	
			num_frames_gain = num_frames_gain - 1
		end				
				
		-- Apply buttons with input delay if necessary				
		local i = 1
		while i <= table.maxn(lag_stack) do
			--emu.print_verbose("ELEMENT " .. lag_stack[i])
			lag_stack[i] = lag_stack[i] - 1	
			if lag_stack[i] <= 0 then
				local key = lag_key[i] 		               
		                local state = button_states[key]
		                if gain_applied then		                	
		             		state[1] = 1
		             	else
		             		state[1] = 0
		             	end		
		                button_states[key] = state
		                table.remove(lag_stack,i)
		                table.remove(lag_key,i)	
		                --emu.print_verbose("removed " .. i)
		        else        					
				i = i + 1
			end	
		end															
			
		for i, state in pairs(button_states) do						
			if state[2].button_offset then
				--emu.print_verbose("button " .. state[2].key_cfg .. " state " .. state[1])
				local offset = guncode_offset(state[2].key_cfg)
				if offset == 1 then
					state[2].button_offset:set_value(state[1])
					state[2].button:set_value(0)	
				else
					state[2].button:set_value(state[1])
					state[2].button_offset:set_value(0)	
				end						
			else
				state[2].button:set_value(state[1])	
			end			        	        		       		       	           			           	        								
		end					
								
	end

	local function load_settings()	
	        --:screen or :mainpcb:screen
	        for i,v in pairs(manager.machine.screens) do 
		      machine_screen = i		         	         
		      break
		end		
	        --emu.print_verbose("machine_screen " .. machine_screen)	
	        save_user_settings()
		local loader = require('gunlight/gunlight_save')
		if loader then
			buttons = loader:load_settings()
		end
	end

	local function save_settings()
		restore_user_settings()	 		
		local saver = require('gunlight/gunlight_save')
		if saver then
			saver:save_settings(buttons)
		end

		menu_handler = nil
		buttons = {}
	end

	local function menu_callback(index, event)
		if menu_handler then
			return menu_handler:handle_menu_event(index, event, buttons)
		else
			return false
		end
	end

	local function menu_populate()
		if not menu_handler then
			menu_handler = require('gunlight/gunlight_menu')
			if menu_handler then
				menu_handler:init_menu(buttons)
			end
		end
		if menu_handler then
			return menu_handler:populate_menu(buttons)
		else
			return {{_p('plugin-gunlight', 'Failed to load gunlight menu'), '', 'off'}}
		end
	end
       
       
        emu.register_frame(process_frame)	
	emu.register_prestart(load_settings)
	emu.register_stop(save_settings)
	emu.register_menu(menu_callback, menu_populate, _p('plugin-gunlight', 'GunLight'))
end

return exports
