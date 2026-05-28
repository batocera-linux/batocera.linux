local frame_num = 0

local function process_frame()
	frame_num = frame_num + 1

	if frame_num == 150 then
		emu.keypost('C')
	end

	if frame_num == 200 then
		manager.machine.cassettes[":cassette"]:play()
	end

	if manager.machine.cassettes[":cassette"].is_stopped == false and manager.machine.cassettes[":cassette"].motor_state == true then
	    manager.machine.video.throttled = false
	    manager.machine.video.frameskip = 12
	else
	    manager.machine.video.throttled = true
	    manager.machine.video.frameskip = 0
	end
end

subscription=emu.add_machine_frame_notifier(process_frame)


