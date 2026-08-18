from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from batocera_common.yaml import safe_dump_yaml12, safe_load_yaml, safe_load_yaml12

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


class TestSafeLoadYaml12:
    def test_loads_simple_mapping(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('foo: bar\nbaz: 1\n')

        result = safe_load_yaml12(file, dict[str, Any])

        assert result == {'foo': 'bar', 'baz': 1}

    def test_loads_sequence(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('- one\n- two\n- three\n')

        result = safe_load_yaml12(file, list[str])

        assert result == ['one', 'two', 'three']

    def test_loads_nested_structure(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('top:\n  inner:\n    - 1\n    - 2\n  flag: true\n')

        result = safe_load_yaml12(file, dict[str, Any])

        assert result == {'top': {'inner': [1, 2], 'flag': True}}

    def test_loads_scalar(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('42\n')

        result = safe_load_yaml12(file, int)

        assert result == 42

    def test_empty_file_returns_none(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('')

        result = safe_load_yaml12(file, dict[str, Any])

        assert result is None

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        file = tmp_path / 'missing.yaml'

        with pytest.raises(FileNotFoundError):
            safe_load_yaml12(file, dict[str, Any])

    def test_uses_safe_pure_loader(self, tmp_path: Path, mocker: MockerFixture) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('foo: bar\n')

        yaml_cls = mocker.patch('ruamel.yaml.YAML')
        yaml_cls.return_value.load.return_value = {'foo': 'bar'}

        result = safe_load_yaml12(file, dict[str, Any])

        yaml_cls.assert_called_once_with(typ='safe', pure=True)
        yaml_cls.return_value.load.assert_called_once()
        assert result == {'foo': 'bar'}


class TestSafeDumpYaml12:
    def test_dump_roundtrip(self, tmp_path: Path) -> None:
        file = tmp_path / 'out.yaml'
        data = {
            'string': 'hello',
            'int': 42,
            'float': 3.14,
            'bool': True,
            'list': [1, 2, 3],
            'nested': {'a': [{'b': 'c'}]},
        }

        safe_dump_yaml12(data, file)
        loaded = safe_load_yaml12(file, dict[str, Any])

        assert loaded == data

    def test_dump_creates_file(self, tmp_path: Path) -> None:
        file = tmp_path / 'out.yaml'
        assert not file.exists()

        safe_dump_yaml12({'a': 1}, file)

        assert file.exists()
        assert file.read_text().strip() != ''

    def test_dump_uses_safe_pure_yaml_and_forwards_data(self, tmp_path: Path, mocker: MockerFixture) -> None:
        file = tmp_path / 'out.yaml'

        yaml_cls = mocker.patch('ruamel.yaml.YAML')
        instance = yaml_cls.return_value

        safe_dump_yaml12({'foo': 'bar'}, file)

        yaml_cls.assert_called_once_with(typ='safe', pure=True)
        instance.dump.assert_called_once_with({'foo': 'bar'}, file)

    def test_dump_with_none_options_leaves_yaml_attributes_untouched(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        file = tmp_path / 'out.yaml'

        yaml_cls = mocker.patch('ruamel.yaml.YAML')
        instance = yaml_cls.return_value
        # Provide sentinel attribute values to assert they are NOT overwritten
        instance.default_flow_style = 'sentinel-flow'
        instance.sort_base_mapping_type_on_output = 'sentinel-sort'
        instance.explicit_start = 'sentinel-start'
        instance.explicit_end = 'sentinel-end'

        safe_dump_yaml12(
            {'foo': 'bar'},
            file,
            flow_style=None,
            sort_mapping=None,
            mapping_indent=None,
            sequence_indent=None,
            sequence_dash_offset=None,
            explicit_start=None,
            explicit_end=None,
        )

        instance.indent.assert_called_once_with(mapping=None, sequence=None, offset=None)
        assert instance.default_flow_style == 'sentinel-flow'
        assert instance.sort_base_mapping_type_on_output == 'sentinel-sort'
        assert instance.explicit_start == 'sentinel-start'
        assert instance.explicit_end == 'sentinel-end'

    def test_dump_forwards_all_options_to_yaml(self, tmp_path: Path, mocker: MockerFixture) -> None:
        file = tmp_path / 'out.yaml'

        yaml_cls = mocker.patch('ruamel.yaml.YAML')
        instance = yaml_cls.return_value

        safe_dump_yaml12(
            {'foo': 'bar'},
            file,
            flow_style=True,
            sort_mapping=True,
            mapping_indent=3,
            sequence_indent=5,
            sequence_dash_offset=1,
            explicit_start=True,
            explicit_end=True,
        )

        instance.indent.assert_called_once_with(mapping=3, sequence=5, offset=1)
        assert instance.default_flow_style is True
        assert instance.sort_base_mapping_type_on_output is True
        assert instance.explicit_start is True
        assert instance.explicit_end is True

    def test_dump_uses_default_options_when_unspecified(self, tmp_path: Path, mocker: MockerFixture) -> None:
        file = tmp_path / 'out.yaml'

        yaml_cls = mocker.patch('ruamel.yaml.YAML')
        instance = yaml_cls.return_value

        safe_dump_yaml12({'foo': 'bar'}, file)

        instance.indent.assert_called_once_with(mapping=2, sequence=4, offset=2)
        assert instance.default_flow_style is False
        assert instance.sort_base_mapping_type_on_output is False


class TestSafeLoadYaml:
    def test_loads_simple_mapping(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('foo: bar\nbaz: 1\n')

        result = safe_load_yaml(file, dict[str, Any])

        assert result == {'foo': 'bar', 'baz': 1}

    def test_loads_sequence(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('- a\n- b\n')

        result = safe_load_yaml(file, list[str])

        assert result == ['a', 'b']

    def test_loads_nested_structure(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('a:\n  b:\n    - 1\n    - 2\n')

        result = safe_load_yaml(file, dict[str, Any])

        assert result == {'a': {'b': [1, 2]}}

    def test_empty_file_returns_none(self, tmp_path: Path) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('')

        result = safe_load_yaml(file, dict[str, Any])

        assert result is None

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        file = tmp_path / 'missing.yaml'

        with pytest.raises(FileNotFoundError):
            safe_load_yaml(file, dict[str, Any])

    def test_delegates_to_pyyaml_safe_load(self, tmp_path: Path, mocker: MockerFixture) -> None:
        file = tmp_path / 'data.yaml'
        file.write_text('foo: bar\n')

        safe_load = mocker.patch('yaml.safe_load', return_value={'foo': 'bar'})

        result = safe_load_yaml(file, dict[str, Any])

        safe_load.assert_called_once_with('foo: bar\n')
        assert result == {'foo': 'bar'}
