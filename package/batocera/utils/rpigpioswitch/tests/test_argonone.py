"""Exercise Argon ONE profiles and button events without touching hardware."""
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, Mock, call, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'rpi-argonone.py'
SOURCE = compile(SCRIPT.read_text(), str(SCRIPT), 'exec')
RISING, FALLING = 'rising', 'falling'


class EndLoop(BaseException):
    """Stop daemon loops without hiding failures in their exception handlers."""


class ArgonOneTests(unittest.TestCase):
    def setUp(self):
        self.bus = Mock(spec=['write_byte', 'write_byte_data', 'close'])
        self.smbus = SimpleNamespace(SMBus=Mock(return_value=self.bus))
        self.gpio = MagicMock()
        self.gpio.EdgeEvent.Type.RISING_EDGE = RISING
        self.gpio.EdgeEvent.Type.FALLING_EDGE = FALLING
        self.files = {
            '/usr/share/batocera/batocera.arch': 'bcm2711\n',
            '/sys/class/thermal/thermal_zone0/temp': '60000\n',
        }

        def open_file(filename, *args, **kwargs):
            if str(filename) not in self.files:
                raise FileNotFoundError(filename)
            return io.StringIO(self.files[str(filename)])

        modules = {
            'smbus': self.smbus,
            'gpiod': self.gpio,
            'gpiod.line': SimpleNamespace(Edge=SimpleNamespace(FALLING=FALLING)),
        }
        for patcher in [
            patch.dict(sys.modules, modules),
            patch.object(sys, 'argv', [str(SCRIPT), 'test']),
            patch('builtins.open', side_effect=open_file),
            patch('os.path.exists', return_value=True),
        ]:
            patcher.start()
            self.addCleanup(patcher.stop)
        self.module = ModuleType('argonone_under_test')
        exec(SOURCE, self.module.__dict__)
        self.bus.reset_mock()
        self.smbus.SMBus.reset_mock()

    def controller(self, profile):
        return self.module.ArgonOneController(self.bus, profile)

    def test_auto_profile_preserves_architecture_defaults(self):
        self.assertEqual(self.module.resolve_profile('auto', 'bcm2711'), 'legacy')
        self.assertEqual(self.module.resolve_profile('auto', 'bcm2712'), 'register')

    def test_explicit_i2c_profile_overrides_architecture_default(self):
        for arch in ['bcm2711', 'bcm2712']:
            for profile in ['legacy', 'register']:
                with self.subTest(arch=arch, profile=profile):
                    self.assertEqual(self.module.resolve_profile(profile, arch), profile)

    def test_invalid_profile_or_unsupported_native_board_is_rejected(self):
        for profile, arch in [('unknown', 'bcm2711'), ('native', 'bcm2711'), ('auto', 'x86_64')]:
            with self.subTest(profile=profile, arch=arch), self.assertRaises(ValueError):
                self.module.resolve_profile(profile, arch)

    def test_fan_commands_and_stop_use_the_selected_protocol(self):
        for profile in ['legacy', 'register']:
            for speed in [0, 30, 55, 100]:
                with self.subTest(profile=profile, speed=speed):
                    self.bus.reset_mock()
                    self.controller(profile).set_fan_speed(speed)
                    expected = call.write_byte(0x1a, speed) if profile == 'legacy' else call.write_byte_data(0x1a, 0x80, speed)
                    self.assertEqual(self.bus.mock_calls, [expected])

    def test_poweroff_uses_the_selected_protocol(self):
        self.controller('legacy').poweroff()
        self.assertEqual(self.bus.mock_calls, [call.write_byte(0x1a, 0xff)])
        self.bus.reset_mock()
        self.controller('register').poweroff()
        self.assertEqual(self.bus.mock_calls, [call.write_byte_data(0x1a, 0x86, 1)])

    def test_invalid_fan_speed_never_reaches_hardware(self):
        for speed in [-1, 101, 0xff]:
            with self.subTest(speed=speed), self.assertRaises(ValueError):
                self.controller('legacy').set_fan_speed(speed)
        self.assertEqual(self.bus.mock_calls, [])

    def test_default_and_custom_temperature_curves(self):
        for temp, expected in [(45000, 0), (55000, 10), (60000, 55), (65000, 100)]:
            with self.subTest(temp=temp):
                self.files['/sys/class/thermal/thermal_zone0/temp'] = str(temp)
                fan = Mock()
                with patch('time.sleep', side_effect=EndLoop), self.assertRaises(EndLoop):
                    self.module.temp_check(fan)
                fan.set_fan_speed.assert_called_once_with(expected)
        self.files['/userdata/system/configs/argonone.conf'] = '# Curve\n48=30\n53=50\n58=70\n63=85\n68=100\n'
        self.files['/sys/class/thermal/thermal_zone0/temp'] = '60000'
        fan = Mock()
        with patch('time.sleep', side_effect=EndLoop), self.assertRaises(EndLoop):
            self.module.temp_check(fan)
        fan.set_fan_speed.assert_called_once_with(70)

    def test_native_actions_need_no_i2c_or_gpio_libraries(self):
        self.files['/usr/share/batocera/batocera.arch'] = 'bcm2712\n'
        with patch.dict(sys.modules, {'smbus': None, 'gpiod': None}), patch('sys.stdout', new_callable=io.StringIO):
            for action in ['start', 'stop', 'halt']:
                with self.subTest(action=action):
                    self.assertEqual(self.module.main([action, 'native']), 0)
        self.smbus.SMBus.assert_not_called()
        self.assertEqual(self.bus.mock_calls, [])

    def test_cli_stop_and_halt_dispatch_and_close_the_bus(self):
        for profile, action, expected in [
            ('legacy', 'stop', call.write_byte(0x1a, 0)),
            ('legacy', 'halt', call.write_byte(0x1a, 0xff)),
            ('register', 'stop', call.write_byte_data(0x1a, 0x80, 0)),
            ('register', 'halt', call.write_byte_data(0x1a, 0x86, 1)),
        ]:
            with self.subTest(profile=profile, action=action):
                self.bus.reset_mock()
                self.assertEqual(self.module.main([action, profile]), 0)
                self.assertEqual(self.bus.mock_calls, [expected, call.close()])

    def test_invalid_cli_and_native_on_pi4_do_not_open_i2c(self):
        for args in [['start', 'invalid'], ['start', 'native'], ['invalid'], ['stop', 'legacy', 'extra']]:
            with self.subTest(args=args), patch('sys.stderr', new_callable=io.StringIO):
                self.assertNotEqual(self.module.main(args), 0)
        self.smbus.SMBus.assert_not_called()

    def test_button_failure_reports_error_and_keeps_fan_active(self):
        with (
            patch.object(self.module, 'Thread') as thread,
            patch.object(self.module, 'shutdown_check', side_effect=RuntimeError('GPIO unavailable')),
            patch('sys.stderr', new_callable=io.StringIO) as stderr,
        ):
            self.assertEqual(self.module.main(['start', 'legacy']), 0)
            thread.return_value.start.assert_called_once()
            thread.return_value.join.assert_called_once()
            self.assertIn('fan control remains active', stderr.getvalue())
            self.bus.close.assert_called_once()

    def test_fan_write_failure_does_not_stop_temperature_loop(self):
        fan = Mock()
        fan.set_fan_speed.side_effect = OSError('I2C unavailable')
        with (
            patch('time.sleep', side_effect=EndLoop),
            patch('sys.stderr', new_callable=io.StringIO) as stderr,
            self.assertRaises(EndLoop),
        ):
            self.module.temp_check(fan)
        self.assertIn('Could not set fan speed', stderr.getvalue())

    def events(self, width_ms, sequence=1, start_ns=1_000_000_000):
        return [
            SimpleNamespace(event_type=RISING, timestamp_ns=start_ns, line_seqno=sequence),
            SimpleNamespace(event_type=FALLING, timestamp_ns=start_ns + int(width_ms * 1_000_000), line_seqno=sequence + 1),
        ]

    def run_button_events(self, batches):
        request = MagicMock()
        request.read_edge_events.side_effect = [*batches, EndLoop()]
        self.gpio.request_lines.return_value.__enter__.return_value = request
        with patch.object(self.module, 'find_gpiochip', return_value='/dev/gpiochip7'):
            try:
                self.module.shutdown_check(self.controller('legacy'), self.gpio)
            except EndLoop:
                pass

    def test_double_click_pulse_boundaries_exit_the_emulator(self):
        for width in [20, 25, 30]:
            with self.subTest(width=width), patch('os.system') as system:
                self.run_button_events([self.events(width)])
                system.assert_called_once_with('/usr/bin/batocera-es-swissknife --emukill')
                self.assertEqual(self.bus.mock_calls, [])

    def test_forced_reboot_stops_fan_and_reboots(self):
        self.module.FORCE_REBOOT = 1
        with patch('os.system', return_value=10 << 8) as system:
            self.run_button_events([self.events(25)])
            self.assertEqual(self.bus.mock_calls, [call.write_byte(0x1a, 0)])
            system.assert_called_once_with('/usr/bin/batocera-es-swissknife --reboot')

    def test_shutdown_pulse_requests_shutdown_without_cutting_power(self):
        for width in [40, 45, 50]:
            with self.subTest(width=width), patch('os.system', return_value=11 << 8) as system:
                self.run_button_events([self.events(width)])
                system.assert_called_once_with('/usr/bin/batocera-es-swissknife --shutdown')
                self.assertEqual(self.bus.mock_calls, [])

    def test_power_action_falls_back_when_emulationstation_is_absent(self):
        for action, command in [('shutdown', 'shutdown -h now'), ('reboot', 'shutdown -r now')]:
            with self.subTest(action=action), patch('os.system', side_effect=[21 << 8, 0]) as system:
                self.assertTrue(self.module.request_power_action(action))
                self.assertEqual(system.call_args_list, [
                    call('/usr/bin/batocera-es-swissknife --' + action), call(command),
                ])

    def test_power_action_accepts_swissknife_success_statuses(self):
        for action, status in [('shutdown', 11 << 8), ('reboot', 10 << 8)]:
            with self.subTest(action=action), patch('os.system', return_value=status) as system:
                self.assertTrue(self.module.request_power_action(action))
                system.assert_called_once()

    def test_failed_shutdown_keeps_monitoring_later_button_pulses(self):
        with (
            patch('os.system', side_effect=[21 << 8, 1 << 8, 11 << 8]) as system,
            patch('sys.stderr', new_callable=io.StringIO),
        ):
            self.run_button_events([self.events(45), self.events(45, sequence=3, start_ns=2_000_000_000)])
            self.assertEqual(system.call_args_list, [
                call('/usr/bin/batocera-es-swissknife --shutdown'),
                call('shutdown -h now'),
                call('/usr/bin/batocera-es-swissknife --shutdown'),
            ])

    def test_failed_reboot_does_not_turn_into_emulator_exit(self):
        self.module.FORCE_REBOOT = 1
        with (
            patch('os.system', side_effect=[21 << 8, 1 << 8, 10 << 8]) as system,
            patch('sys.stderr', new_callable=io.StringIO),
        ):
            self.run_button_events([self.events(25), self.events(25, sequence=3, start_ns=2_000_000_000)])
            self.assertEqual(system.call_args_list, [
                call('/usr/bin/batocera-es-swissknife --reboot'),
                call('shutdown -r now'),
                call('/usr/bin/batocera-es-swissknife --reboot'),
            ])

    def test_noise_startup_falling_and_missing_edges_are_ignored(self):
        for width in [0, 19, 31, 39, 51, 60, 70, 1000, -25]:
            with self.subTest(width=width), patch('os.system') as system:
                self.run_button_events([self.events(width)])
                system.assert_not_called()
        with patch('os.system') as system:
            self.run_button_events([[self.events(25)[1]]])
            missing_edge = self.events(25)
            missing_edge[1].line_seqno += 1
            self.run_button_events([missing_edge])
            system.assert_not_called()

    def test_batched_and_split_pulses_are_processed_once(self):
        events = self.events(25) + self.events(25, sequence=3, start_ns=2_000_000_000)
        with patch('os.system') as system:
            self.run_button_events([events[:1], events[1:]])
            self.assertEqual(system.call_count, 2)

    def test_gpio_discovery_uses_header_identity_not_chip_number(self):
        chips = {}
        for path, label, line in [
            ('/dev/gpiochip0', 'unrelated', 'GPIO4'),
            ('/dev/gpiochip1', 'raspberrypi-exp-gpio', 'VDD_SD_IO_SEL'),
            ('/dev/gpiochip7', 'pinctrl-rp1', 'GPIO4'),
        ]:
            chip = MagicMock()
            chip.__enter__.return_value = chip
            chip.get_info.return_value = SimpleNamespace(label=label, num_lines=54)
            chip.get_line_info.return_value = SimpleNamespace(name=line)
            chips[path] = chip
        self.gpio.Chip.side_effect = chips.__getitem__
        with patch.object(self.module.glob, 'glob', return_value=list(chips)):
            self.assertEqual(self.module.find_gpiochip(self.gpio), '/dev/gpiochip7')
        with patch.object(self.module.glob, 'glob', return_value=[]), self.assertRaises(RuntimeError):
            self.module.find_gpiochip(self.gpio)
        chips['/dev/gpiochip8'] = chips['/dev/gpiochip7']
        with patch.object(self.module.glob, 'glob', return_value=list(chips)), self.assertRaises(RuntimeError):
            self.module.find_gpiochip(self.gpio)


if __name__ == '__main__':
    unittest.main()
