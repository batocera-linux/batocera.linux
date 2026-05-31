from __future__ import annotations

from batocera_common.configparser import (
    CaseSensitiveConfigParser,
    CaseSensitiveRawConfigParser,
)


class TestCaseSensitiveRawConfigParser:
    def test_preserves_option_case_on_set_and_get(self) -> None:
        parser = CaseSensitiveRawConfigParser()
        parser.add_section('section')
        parser.set('section', 'MixedCaseKey', 'value')

        assert parser.get('section', 'MixedCaseKey') == 'value'
        assert parser.options('section') == ['MixedCaseKey']

    def test_preserves_option_case_when_reading_string(self) -> None:
        parser = CaseSensitiveRawConfigParser()
        parser.read_string('[section]\nMixedCaseKey = value\nAnother = 1\n')

        assert parser.options('section') == ['MixedCaseKey', 'Another']
        assert parser.get('section', 'MixedCaseKey') == 'value'

    def test_distinct_keys_with_different_case(self) -> None:
        parser = CaseSensitiveRawConfigParser()
        parser.add_section('section')
        parser.set('section', 'Key', 'one')
        parser.set('section', 'key', 'two')
        parser.set('section', 'KEY', 'three')

        assert parser.get('section', 'Key') == 'one'
        assert parser.get('section', 'key') == 'two'
        assert parser.get('section', 'KEY') == 'three'


class TestCaseSensitiveConfigParser:
    def test_preserves_option_case_on_set_and_get(self) -> None:
        parser = CaseSensitiveConfigParser()
        parser.add_section('section')
        parser.set('section', 'MixedCaseKey', 'value')

        assert parser.get('section', 'MixedCaseKey') == 'value'
        assert parser.options('section') == ['MixedCaseKey']

    def test_preserves_option_case_when_reading_string(self) -> None:
        parser = CaseSensitiveConfigParser()
        parser.read_string('[section]\nMixedCaseKey = value\nAnother = 1\n')

        assert parser.options('section') == ['MixedCaseKey', 'Another']
        assert parser.get('section', 'MixedCaseKey') == 'value'

    def test_supports_interpolation_with_case_sensitive_keys(self) -> None:
        parser = CaseSensitiveConfigParser()
        parser.read_string('[section]\nBase = hello\nGreeting = %(Base)s world\n')

        assert parser.get('section', 'Greeting') == 'hello world'
