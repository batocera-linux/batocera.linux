--local button = {}
--print("=== Ports ===")
--for i, j in pairs(manager.machine.ioport.ports) do
-- for field_name, field in pairs(j.fields) do
--  id = field.port.tag .. ',' .. field.mask .. ',' .. field.type
--  print(field_name,": ", id)
--  button[id] = field
-- end
--end

print("")
print("=== Cassettes ===")
for i, j in pairs(manager.machine.cassettes) do
 print(i)
end

print("")
print("=== Images ===")
for i, j in pairs(manager.machine.images) do
 print(i)
end

part = {}
table.insert(part, os.getenv("RANDOMAME_PART_1"))
table.insert(part, os.getenv("RANDOMAME_PART_2"))
--table.insert(part, os.getenv("RANDOMAME_PART_3"))

feature = {}
table.insert(feature, os.getenv("RANDOMAME_PART_FEATURE_1"))
table.insert(feature, os.getenv("RANDOMAME_PART_FEATURE_2"))
--table.insert(feature, os.getenv("RANDOMAME_PART_FEATURE_3"))

commands = {}

for i,p in ipairs(part) do
    my_feature = table.remove(feature,1)
    if my_feature == nil then
        table.insert(commands, "LOAD")
    else
        if my_feature == 'part_id:BG Data' then
            table.insert(commands, "LOADS")
        else
            table.insert(commands, "LOAD")
        end
    end
end

local frame_num = 0
local current_command = nil
local run_end_frame = 0

local function process_frame()
        frame_num = frame_num + 1

        if frame_num > run_end_frame + 100 then
            if current_command == nil then
                current_command = table.remove(commands,1)
                if current_command == "LOADS" then
                    manager.machine.images[":exp:fc_keyboard:tape"]:load_software(table.remove(part,1))
                    emu.keypost("LOADS\n")
                    manager.machine.cassettes[":exp:fc_keyboard:tape"]:play()
                elseif current_command == "LOAD" then
                    manager.machine.images[":exp:fc_keyboard:tape"]:load_software(table.remove(part,1))
                    emu.keypost("LOAD\n")
                    manager.machine.cassettes[":exp:fc_keyboard:tape"]:play()
                end
            end
        end

		if manager.machine.cassettes[":exp:fc_keyboard:tape"].is_stopped == false and manager.machine.cassettes[":exp:fc_keyboard:tape"].motor_state == true then
            manager.machine.video.throttled = false
	        manager.machine.video.frameskip = 12
		else
		    manager.machine.video.throttled = true
		    manager.machine.video.frameskip = 0

            if current_command ~= nil then
    		    if current_command == "LOADS" then
	    	        current_command = nil
		        elseif current_command == "LOAD" then
    		        current_command = nil
		             -- if next command is a "LOAD", issue a "RUN" and wait for its execution
		            if commands[1] == "LOAD" then
       		            emu.keypost("RUN\n")
		                run_end_frame = frame_num + 800
	    	        end
    		    end

	            -- if last command, issue a "RUN"
                if commands[1] == nil then
	                emu.keypost("RUN\n")
	            end
	        end
		end
end

subscription=emu.add_machine_frame_notifier(process_frame)
