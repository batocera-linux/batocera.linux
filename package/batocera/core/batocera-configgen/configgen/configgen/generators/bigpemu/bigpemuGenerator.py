#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import subprocess
import sys
import shutil
import stat
import configparser
import filecmp
from utils.logger import get_logger

eslog = get_logger(__name__)

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        wineprefix = "/userdata/system/wine-bottles/jaguar"
        emupath = wineprefix + "/bigpemu"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        #copy bigpemu files to wine bottle
        if not os.path.exists(emupath):
            shutil.copytree("/usr/bigpemu", emupath)
        
        # check we have the latest version in the wine bottle
        if not filecmp.cmp("/usr/bigpemu/BigPEmu.exe", emupath + "/BigPEmu.exe"):
            shutil.copytree("/usr/bigpemu", emupath, dirs_exist_ok=True)

        # install windows libraries required
        if not os.path.exists(wineprefix + "/d3dcompiler_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dcompiler_43"]
            env = {"LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/ge-custom/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/ge-custom/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dcompiler_43.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dx9_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9_43"]
            env = {"LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/ge-custom/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/ge-custom/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9_43.done", "w") as f:
                f.write("done")
    
        if not os.path.exists(wineprefix + "/d3dx9.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9"]
            env = {"LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/ge-custom/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/ge-custom/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9.done", "w") as f:
                f.write("done")
      
        # todo: some config?
        # /userdata/saves/bigpemu-bottle/drive_c/users/root/AppData/Roaming/BigPEmu/BigPEmuConfig.bigpcfg

        # now run the emulator
        commandArray = ["/usr/wine/ge-custom/bin/wine", emupath + "/BigPEmu.exe", rom]

        environment={
            "WINEPREFIX": wineprefix,
            "LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/ge-custom/lib/wine",
            "LIBGL_DRIVERS_PATH": "/usr/lib/dri:/lib32/dri",
            "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
            "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
        }
        # ensure nvidia driver used for vulkan
        if os.path.exists('/var/tmp/nvidia.prime'):
            variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
            for variable_name in variables_to_remove:
                if variable_name in os.environ:
                    del os.environ[variable_name]

            environment.update(
                {
                    'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                    'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d'
                }
            )
        # we use a 64-bit wine bottle
        return Command.Command(
            array=commandArray,
            env=environment
        )
