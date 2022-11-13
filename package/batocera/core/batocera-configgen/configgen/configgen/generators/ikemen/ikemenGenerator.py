import Command
from generators.Generator import Generator
from utils.logger import get_logger
import controllersConfig
import json
import os

eslog = get_logger(__name__)

Keymapping =[
        {
			"Joystick": -1,
			"Buttons": [
				"UP",
				"DOWN",
				"LEFT",
				"RIGHT",
				"a",
				"s",
				"d",
				"z",
				"x",
				"c",
				"RETURN",
				"f",
				"v",
				"q"
			]
		},
		{
			"Joystick": -1,
			"Buttons": [
				"KP_8",
				"KP_5",
				"KP_4",
				"KP_6",
				"p",
				"LBRACKET",
				"RBRACKET",
				"SEMICOLON",
				"QUOTE",
				"BACKSLASH",
				"SLASH",
				"o",
				"l",
				"PERIOD"
			]
		},
		{
			"Joystick": -1,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
		{
			"Joystick": -1,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		}
	]

Joymapping =[
        {
			"Joystick": 0,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
        {
			"Joystick": 1,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
		{
			"Joystick": 2,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
		{
			"Joystick": 3,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		}
	]

class IkemenGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        try:
            conf = json.load(open(rom+"/save/config.json", "r"))
        except:
            conf = {}

        # Joystick configuration seems completely broken in 0.98.2 Linux
        # so let's force keyboad and use a pad2key
        conf["KeyConfig"] = Keymapping
        conf["JoystickConfig"] = Joymapping
        conf["Fullscreen"] = True

        js_out = json.dumps(conf, indent=2)
        if not os.path.isdir(rom+"/save"):
            os.mkdir(rom+"/save")
        with open(rom+"/save/config.json", "w") as jout:
            jout.write(js_out)

        commandArray = ["/usr/bin/batocera-ikemen", rom]

        return Command.Command(array=commandArray, env={ "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers) })
