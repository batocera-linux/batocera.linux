from __future__ import annotations

from pathlib import Path

import pytest

from batocera_common.key_value_config import KeyValueConfig

pytestmark = pytest.mark.usefixtures('fs')


class TestKeyValueConfigGetSet:
    def test_set_and_get_item(self) -> None:
        config = KeyValueConfig()
        config['foo'] = 'bar'
        assert config['foo'] == 'bar'

    def test_get_with_default(self) -> None:
        config = KeyValueConfig()
        assert config.get('missing') is None
        assert config.get('missing', 'fallback') == 'fallback'

    def test_get_existing_key(self) -> None:
        config = KeyValueConfig()
        config['foo'] = 'bar'
        assert config.get('foo') == 'bar'
        assert config.get('foo', 'fallback') == 'bar'

    def test_contains(self) -> None:
        config = KeyValueConfig()
        config['foo'] = 'bar'
        assert 'foo' in config
        assert 'missing' not in config

    def test_delitem(self) -> None:
        config = KeyValueConfig()
        config['foo'] = 'bar'
        del config['foo']
        assert 'foo' not in config

    def test_preserves_key_case(self) -> None:
        config = KeyValueConfig()
        config['MixedCase'] = 'value'
        assert config['MixedCase'] == 'value'
        assert 'mixedcase' not in config


class TestKeyValueConfigReadWrite:
    def test_write_and_read_roundtrip(self) -> None:
        path = Path('/config.cfg')
        config = KeyValueConfig()
        config['a'] = '1'
        config['b'] = 'two'
        config.write(path)

        loaded = KeyValueConfig()
        loaded.read(path)

        assert loaded['a'] == '1'
        assert loaded['b'] == 'two'
        assert path.read_text() == 'a=1\nb=two\n'

    def test_write_with_separator(self) -> None:
        path = Path('/config.cfg')
        config = KeyValueConfig(' ')
        config['key'] = 'value'
        config.write(path)

        assert path.read_text() == 'key = value\n'

    def test_read_missing_file_does_not_raise(self) -> None:
        config = KeyValueConfig()
        config.read('/does/not/exist.cfg')
        assert config.get('anything') is None

    def test_read_updates_existing_keys(self) -> None:
        path = Path('/config.cfg')
        path.write_text('from_file=yes\n', encoding='latin1')

        config = KeyValueConfig()
        config['from_file'] = 'no'
        config['other'] = 'kept'
        config.read(path)

        assert config['from_file'] == 'yes'
        assert config['other'] == 'kept'

    def test_read_latin1_content(self) -> None:
        path = Path('/config.cfg')
        path.write_bytes(b'name=caf\xe9\n')

        config = KeyValueConfig()
        config.read(path)

        assert config['name'] == 'café'


class TestKeyValueConfigSection:
    def test_section_returns_matching_keys(self) -> None:
        config = KeyValueConfig()
        config['global.shader'] = 'crt'
        config['global.smooth'] = '1'
        config['nes.core'] = 'fceumm'

        assert config.section('global') == {'shader': 'crt', 'smooth': '1'}
        assert config.section('nes') == {'core': 'fceumm'}

    def test_section_items_is_iterator(self) -> None:
        config = KeyValueConfig()
        config['global.a'] = '1'
        config['global.b'] = '2'

        assert list(config.section_items('global')) == [('a', '1'), ('b', '2')]

    def test_section_skips_default_values_by_default(self) -> None:
        config = KeyValueConfig()
        config['sys.a'] = 'keep'
        config['sys.b'] = ''
        config['sys.c'] = 'default'
        config['sys.d'] = 'auto'

        assert config.section('sys') == {'a': 'keep'}

    def test_section_keep_defaults(self) -> None:
        config = KeyValueConfig()
        config['sys.a'] = 'keep'
        config['sys.b'] = ''
        config['sys.c'] = 'default'
        config['sys.d'] = 'auto'

        assert config.section('sys', keep_defaults=True) == {
            'a': 'keep',
            'b': '',
            'c': 'default',
            'd': 'auto',
        }

    def test_section_with_special_characters(self) -> None:
        config = KeyValueConfig()
        config['nes["Game Name"].shader'] = 'crt'
        config['nes["Game Name"].smooth'] = '1'
        config['nes.core'] = 'fceumm'

        assert config.section('nes["Game Name"]') == {'shader': 'crt', 'smooth': '1'}

    def test_section_with_folder_path(self) -> None:
        config = KeyValueConfig()
        config['snes.folder["/userdata/roms/snes"].ratio'] = 'core'
        config['snes.ratio'] = 'auto'

        assert config.section('snes.folder["/userdata/roms/snes"]', keep_defaults=True) == {
            'ratio': 'core',
        }

    def test_empty_section(self) -> None:
        config = KeyValueConfig()
        config['other.key'] = 'value'
        assert config.section('missing') == {}


class TestKeyValueConfigRemove:
    def test_remove_all_starting_with(self) -> None:
        config = KeyValueConfig()
        config['foo.a'] = '1'
        config['foo.b'] = '2'
        config['foobar'] = '3'
        config['bar'] = '4'

        config.remove_all_starting_with('foo')

        assert 'foo.a' not in config
        assert 'foo.b' not in config
        assert 'foobar' not in config
        assert config['bar'] == '4'

    def test_remove_section(self) -> None:
        config = KeyValueConfig()
        config['sys.a'] = '1'
        config['sys.b'] = '2'
        config['sysextra'] = '3'
        config['other'] = '4'

        config.remove_section('sys')

        assert 'sys.a' not in config
        assert 'sys.b' not in config
        assert config['sysextra'] == '3'
        assert config['other'] == '4'
