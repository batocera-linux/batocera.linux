"""Run the real Argon launcher functions against temporary files and fake commands."""
from __future__ import annotations

import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'rpi_gpioswitch.sh'
TEXT = SCRIPT.read_text()
FUNCTIONS = TEXT[TEXT.index('# Pi4:'):TEXT.index('#https://www.kintaro.co')]


class ArgonLauncherTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.boot = self.root / 'config.txt'
        self.boot.write_text('# Existing boot settings\n')
        self.arch = self.root / 'arch'
        self.arch.write_text('bcm2711\n')
        self.state = self.root / 'argonone.profile'
        self.flag = self.root / 'shutdown.please'
        self.settings = self.root / 'setting'
        self.settings.write_text('legacy\n')
        self.log = self.root / 'commands'
        self.daemon = self.root / 'daemon'
        self.daemon.write_text('#!/bin/sh\nprintf "daemon %s\\n" "$*" >> ' + shlex.quote(str(self.log)) + '\n')
        self.daemon.chmod(0o755)
        self.get_settings = self.root / 'settings-get'
        self.get_settings.write_text('#!/bin/sh\ncat ' + shlex.quote(str(self.settings)) + '\n')
        self.get_settings.chmod(0o755)
        self.functions = FUNCTIONS
        for old, new in {
            '/boot/config.txt': self.boot,
            '/usr/share/batocera/batocera.arch': self.arch,
            '/usr/bin/rpi-argonone': self.daemon,
            '/usr/bin/batocera-settings-get': self.get_settings,
            '/var/run/argonone.profile': self.state,
            '/tmp/shutdown.please': self.flag,
        }.items():
            self.functions = self.functions.replace(old, str(new))
        self.assertNotIn('/boot/', self.functions)
        self.assertNotIn('/var/run/', self.functions)

    def run_launcher(self, action, config=False, pid=''):
        log = shlex.quote(str(self.log))
        prelude = '\n'.join([
            'CONF=' + ('1' if config else '0'),
            f'mount() {{ printf "mount\\n" >> {log}; }}',
            f'modprobe() {{ printf "modprobe %s\\n" "$*" >> {log}; }}',
            f'pgrep() {{ printf "%s" {shlex.quote(pid)}; }}',
            f'kill() {{ printf "kill %s\\n" "$*" >> {log}; }}',
        ])
        result = subprocess.run(['bash', '-c', prelude + '\n' + self.functions + '\nargonone_' + action],
                                text=True, capture_output=True, timeout=5)
        self.commands = self.log.read_text() if self.log.exists() else ''
        return result

    def test_start_passes_profile_and_saves_it(self):
        result = self.run_launcher('start')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('daemon start legacy\n', self.commands)
        self.assertEqual(self.state.read_text().strip(), 'legacy')

    def test_native_start_and_config_leave_boot_and_hardware_alone(self):
        self.settings.write_text('native\n')
        self.arch.write_text('bcm2712\n')
        original = self.boot.read_text()
        for config in [True, False]:
            with self.subTest(config=config):
                result = self.run_launcher('start', config=config)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.boot.read_text(), original)
                self.assertEqual(self.commands, '')
        self.assertEqual(self.state.read_text().strip(), 'native')

    def test_invalid_profile_and_native_pi4_do_not_modify_boot(self):
        original = self.boot.read_text()
        for profile in ['wrong', 'native']:
            with self.subTest(profile=profile):
                self.settings.write_text(profile + '\n')
                result = self.run_launcher('start')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.boot.read_text(), original)
                self.assertEqual(self.commands, '')

    def test_config_prepares_i2c_without_starting_daemon(self):
        result = self.run_launcher('start', config=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('dtparam=i2c_arm=on', self.boot.read_text())
        self.assertNotIn('daemon', self.commands)
        self.assertNotIn('modprobe', self.commands)
        self.assertFalse(self.state.exists())

    def test_stop_uses_running_profile_after_config_edit(self):
        self.state.write_text('register\n')
        result = self.run_launcher('stop')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('daemon stop register\n', self.commands)
        self.assertFalse(self.state.exists())

    def test_halt_uses_running_profile(self):
        self.state.write_text('register\n')
        self.flag.touch()
        result = self.run_launcher('stop')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('daemon halt register\n', self.commands)

    def test_native_stop_cleans_old_daemon_without_i2c(self):
        self.state.write_text('native\n')
        self.arch.write_text('bcm2712\n')
        result = self.run_launcher('stop', pid='1234')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commands, 'kill -9 1234\n')
        self.assertFalse(self.state.exists())

    def test_empty_setting_defaults_to_auto(self):
        self.settings.write_text('')
        result = self.run_launcher('start')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('daemon start auto\n', self.commands)
