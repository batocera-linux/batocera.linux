from __future__ import annotations

from batocera_common.exceptions import flatten_exception_group, flatten_exception_group_iter


class TestFlattenExceptionGroup:
    def test_flat_group_preserves_order(self) -> None:
        first = ValueError('first')
        second = TypeError('second')
        group = ExceptionGroup('flat', [first, second])

        assert flatten_exception_group(group) == [first, second]

    def test_nested_groups_are_flattened_depth_first(self) -> None:
        a = ValueError('a')
        b = TypeError('b')
        c = RuntimeError('c')
        d = KeyError('d')

        group = ExceptionGroup(
            'outer',
            [
                a,
                ExceptionGroup('inner', [b, ExceptionGroup('deeper', [c])]),
                d,
            ],
        )

        assert flatten_exception_group(group) == [a, b, c, d]

    def test_single_leaf_group(self) -> None:
        error = ValueError('only')
        group = ExceptionGroup('one', [error])

        assert flatten_exception_group(group) == [error]

    def test_sibling_nested_groups(self) -> None:
        left = ValueError('left')
        right = TypeError('right')
        group = ExceptionGroup(
            'siblings',
            [
                ExceptionGroup('left-group', [left]),
                ExceptionGroup('right-group', [right]),
            ],
        )

        assert flatten_exception_group(group) == [left, right]


class TestFlattenExceptionGroupIter:
    def test_iter_matches_list_helper(self) -> None:
        group = ExceptionGroup(
            'mixed',
            [
                ValueError('a'),
                ExceptionGroup('nested', [TypeError('b'), RuntimeError('c')]),
            ],
        )

        assert list(flatten_exception_group_iter(group)) == flatten_exception_group(group)

    def test_iter_is_lazy(self) -> None:
        group = ExceptionGroup('two', [ValueError('a'), TypeError('b')])

        iterator = flatten_exception_group_iter(group)

        assert next(iterator) == group.exceptions[0]
        assert next(iterator) == group.exceptions[1]
        assert list(iterator) == []
