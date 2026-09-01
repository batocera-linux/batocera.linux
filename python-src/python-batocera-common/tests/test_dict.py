from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from batocera_common.dict import merge

if TYPE_CHECKING:
    from collections.abc import Mapping


class TestMergeFlat:
    def test_adds_new_keys(self) -> None:
        destination = {'a': 1}
        merge(destination, {'b': 2})
        assert destination == {'a': 1, 'b': 2}

    def test_overwrites_existing_keys(self) -> None:
        destination = {'a': 1, 'b': 2}
        merge(destination, {'b': 3})
        assert destination == {'a': 1, 'b': 3}

    def test_empty_source_leaves_destination_unchanged(self) -> None:
        destination = {'a': 1}
        merge(destination, {})
        assert destination == {'a': 1}

    def test_empty_destination_copies_source(self) -> None:
        destination: dict[str, object] = {}
        merge(destination, {'a': 1, 'b': 2})
        assert destination == {'a': 1, 'b': 2}


class TestMergeNested:
    def test_merges_nested_dicts(self) -> None:
        destination = {'a': {'x': 1, 'y': 2}}
        merge(destination, {'a': {'y': 3, 'z': 4}})
        assert destination == {'a': {'x': 1, 'y': 3, 'z': 4}}

    def test_merges_deeply_nested_dicts(self) -> None:
        destination = {'a': {'b': {'c': 1, 'd': 2}}}
        merge(destination, {'a': {'b': {'d': 3, 'e': 4}}})
        assert destination == {'a': {'b': {'c': 1, 'd': 3, 'e': 4}}}

    def test_adds_nested_dict_for_new_key(self) -> None:
        destination = {'a': 1}
        merge(destination, {'b': {'x': 2}})
        assert destination == {'a': 1, 'b': {'x': 2}}

    def test_replaces_non_dict_with_dict(self) -> None:
        destination = {'a': 1}
        merge(destination, {'a': {'x': 2}})
        assert destination == {'a': {'x': 2}}

    def test_replaces_dict_with_non_dict(self) -> None:
        destination = {'a': {'x': 1}}
        merge(destination, {'a': 2})
        assert destination == {'a': 2}

    def test_replaces_dict_with_list(self) -> None:
        destination = {'a': {'x': 1}}
        merge(destination, {'a': [1, 2]})
        assert destination == {'a': [1, 2]}

    def test_does_not_merge_lists(self) -> None:
        destination = {'a': [1, 2]}
        merge(destination, {'a': [3, 4]})
        assert destination == {'a': [3, 4]}


class TestMergeMappingTypes:
    def test_accepts_mapping_proxy_as_source(self) -> None:
        destination = {'a': {'x': 1}}
        source: Mapping[str, object] = MappingProxyType({'a': {'y': 2}, 'b': 3})
        merge(destination, source)
        assert destination == {'a': {'x': 1, 'y': 2}, 'b': 3}

    def test_merges_mapping_into_nested_dict(self) -> None:
        destination = {'a': {'x': 1}}
        merge(destination, {'a': MappingProxyType({'y': 2})})
        assert destination == {'a': {'x': 1, 'y': 2}}


class TestMergeInPlace:
    def test_mutates_destination_in_place(self) -> None:
        destination = {'a': 1}
        result = merge(destination, {'b': 2})
        assert result is None
        assert destination == {'a': 1, 'b': 2}

    def test_does_not_mutate_source(self) -> None:
        destination = {'a': {'x': 1}}
        source = {'a': {'y': 2}}
        merge(destination, source)
        assert source == {'a': {'y': 2}}

    def test_nested_merge_preserves_destination_subdict_identity(self) -> None:
        nested = {'x': 1}
        destination = {'a': nested}
        merge(destination, {'a': {'y': 2}})
        assert destination['a'] is nested
        assert nested == {'x': 1, 'y': 2}
