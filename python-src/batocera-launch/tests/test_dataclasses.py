from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from batocera_launch.dataclasses import cached_dataclass
from batocera_launch.functools import cached_property

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class TestCachedDataclassDecoratorForms:
    def test_without_parentheses(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

        obj = MyClass(x=1)
        assert obj.x == 1

    def test_with_parentheses(self) -> None:
        @cached_dataclass()
        class MyClass:
            x: int

        obj = MyClass(x=2)
        assert obj.x == 2

    def test_direct_call_with_class(self) -> None:
        class MyClass:
            x: int

        Result = cached_dataclass(MyClass)
        obj = Result(x=3)  # type: ignore[call-arg]  # pyright: ignore
        assert obj.x == 3


class TestCachedDataclassSlots:
    def test_has_slots(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

        assert hasattr(MyClass, '__slots__')

    def test_cannot_set_arbitrary_attributes(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

        obj = MyClass(x=1)
        with pytest.raises(AttributeError):
            obj.y = 2  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]


class TestCachedPropertyBasic:
    def test_computes_value(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        obj = MyClass(x=5)
        assert obj.doubled == 10

    def test_caches_value(self, mocker: MockerFixture) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def computed(self) -> int:
                return self.x * 2

        spy = mocker.spy(MyClass.computed, 'func')

        obj = MyClass(x=5)
        _ = obj.computed
        _ = obj.computed
        _ = obj.computed
        assert spy.call_count == 1

    def test_class_access_returns_descriptor(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        assert isinstance(MyClass.doubled, cached_property)

    def test_excluded_from_init(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        with pytest.raises(TypeError):
            MyClass(x=1, doubled=2)  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]

    def test_excluded_from_repr(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        obj = MyClass(x=5)
        _ = obj.doubled
        assert 'doubled' not in repr(obj)

    def test_excluded_from_eq(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def random_val(self) -> object:
                return object()

        a = MyClass(x=1)
        b = MyClass(x=1)
        _ = a.random_val
        _ = b.random_val
        assert a == b


class TestCachedPropertyDelete:
    def test_delete_allows_recomputation(self, mocker: MockerFixture) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def computed(self) -> int:
                return self.x * 2

        spy = mocker.spy(MyClass.computed, 'func')

        obj = MyClass(x=5)
        assert obj.computed == 10
        assert spy.call_count == 1

        del obj.computed
        assert obj.computed == 10
        assert spy.call_count == 2

    def test_delete_unset_property_does_not_raise(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def computed(self) -> int:
                return self.x * 2

        obj = MyClass(x=5)
        del obj.computed  # never accessed, should not raise


class TestCachedPropertyFrozen:
    def test_works_with_frozen_dataclass(self) -> None:
        @cached_dataclass(frozen=True)
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        obj = MyClass(x=5)
        assert obj.doubled == 10

    def test_caches_with_frozen_dataclass(self, mocker: MockerFixture) -> None:
        @cached_dataclass(frozen=True)
        class MyClass:
            x: int

            @cached_property
            def computed(self) -> int:
                return self.x * 2

        spy = mocker.spy(MyClass.computed, 'func')

        obj = MyClass(x=5)
        _ = obj.computed
        _ = obj.computed
        assert spy.call_count == 1


class TestCachedPropertyMultiple:
    def test_multiple_cached_properties(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

            @cached_property
            def tripled(self) -> int:
                return self.x * 3

        obj = MyClass(x=4)
        assert obj.doubled == 8
        assert obj.tripled == 12

    def test_multiple_cached_properties_independent_caching(self, mocker: MockerFixture) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

            @cached_property
            def tripled(self) -> int:
                return self.x * 3

        doubled_spy = mocker.spy(MyClass.doubled, 'func')
        tripled_spy = mocker.spy(MyClass.tripled, 'func')

        obj = MyClass(x=4)
        _ = obj.doubled
        _ = obj.tripled
        _ = obj.doubled
        _ = obj.tripled
        assert doubled_spy.call_count == 1
        assert tripled_spy.call_count == 1

    def test_delete_one_does_not_affect_other(self, mocker: MockerFixture) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

            @cached_property
            def tripled(self) -> int:
                return self.x * 3

        doubled_spy = mocker.spy(MyClass.doubled, 'func')
        tripled_spy = mocker.spy(MyClass.tripled, 'func')

        obj = MyClass(x=4)
        _ = obj.doubled
        _ = obj.tripled
        del obj.doubled
        _ = obj.doubled
        assert doubled_spy.call_count == 2
        assert tripled_spy.call_count == 1


class TestCachedPropertyWithoutCachedDataclass:
    def test_get_raises_type_error(self) -> None:
        class MyClass:
            @cached_property
            def value(self) -> int:
                return 42

        obj = MyClass()
        with pytest.raises(TypeError, match='cached_property must be used with'):
            _ = obj.value

    def test_delete_raises_type_error(self) -> None:
        class MyClass:
            @cached_property
            def value(self) -> int:
                return 42

        obj = MyClass()
        with pytest.raises(TypeError, match='cached_property must be used with'):
            del obj.value


class TestCachedPropertyMixedFields:
    def test_regular_and_cached_fields(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int
            y: str

            @cached_property
            def combined(self) -> str:
                return f'{self.x}-{self.y}'

        obj = MyClass(x=1, y='hello')
        assert obj.x == 1
        assert obj.y == 'hello'
        assert obj.combined == '1-hello'

    def test_multiple_instances_independent(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        a = MyClass(x=3)
        b = MyClass(x=7)
        assert a.doubled == 6
        assert b.doubled == 14


class TestCachedPropertyDoc:
    def test_preserves_docstring(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                """Return x doubled."""
                return self.x * 2

        assert MyClass.doubled.__doc__ == 'Return x doubled.'

    def test_no_docstring(self) -> None:
        @cached_dataclass
        class MyClass:
            x: int

            @cached_property
            def doubled(self) -> int:
                return self.x * 2

        assert MyClass.doubled.__doc__ is None
