local function process_frame()
		if manager.machine.cassettes[":cassette"].is_stopped == false and manager.machine.cassettes[":cassette"].motor_state == true then
		    manager.machine.video.throttled = false
		    manager.machine.video.frameskip = 12
		else
		    manager.machine.video.throttled = true
		    manager.machine.video.frameskip = 0
		end
end

subscription=emu.add_machine_frame_notifier(process_frame)

emu.keypost('\nj""\n')
manager.machine.cassettes[":cassette"]:play()

