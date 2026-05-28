local function process_frame()
		if manager.machine.cassettes[":cassette"].is_stopped == false and manager.machine.cassettes[":cassette"].motor_state == true then
		    manager.machine.video.throttled = false
		    manager.machine.video.frameskip = 12
		else
		    manager.machine.video.throttled = true
		    manager.machine.video.frameskip = 0
		end
end

info_usage = os.getenv("RANDOMAME_INFO_USAGE")

command = ""
if info_usage == "Load with LOADM" then
    command = 'LOADM\n'
else
    command = 'RUN"\n'
end

emu.keypost(command)
manager.machine.cassettes[":cassette"]:play()

subscription=emu.add_machine_frame_notifier(process_frame)
