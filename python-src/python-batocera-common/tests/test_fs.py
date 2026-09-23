from __future__ import annotations

from pathlib import Path

import pytest

from batocera_common.fs import atomic_write, directory_differences

pytestmark = pytest.mark.usefixtures('fs')


def _write(path: Path, content: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestAtomicWrite:
    def test_creates_file_with_content(self) -> None:
        path = Path('/data/config.txt')
        path.parent.mkdir(parents=True)

        with atomic_write(path) as tmp_path:
            assert tmp_path != path
            assert not path.exists()
            tmp_path.write_text('hello')

        assert path.read_text() == 'hello'
        assert not tmp_path.exists()

    def test_overwrites_existing_file(self) -> None:
        path = Path('/data/config.txt')
        _write(path, 'old')

        with atomic_write(path) as tmp_path:
            tmp_path.write_text('new')

        assert path.read_text() == 'new'
        assert not tmp_path.exists()

    def test_does_not_replace_target_when_body_raises(self) -> None:
        path = Path('/data/config.txt')
        _write(path, 'original')

        with pytest.raises(RuntimeError, match='boom'), atomic_write(path) as tmp_path:  # ruff: ignore[pytest-raises-with-multiple-statements]
            tmp_path.write_text('partial')
            raise RuntimeError('boom')

        assert path.read_text() == 'original'
        assert not tmp_path.exists()

    def test_does_not_create_target_when_body_raises(self) -> None:
        path = Path('/data/config.txt')
        path.parent.mkdir(parents=True)

        with pytest.raises(RuntimeError, match='boom'), atomic_write(path) as tmp_path:  # ruff: ignore[pytest-raises-with-multiple-statements]
            tmp_path.write_text('partial')
            raise RuntimeError('boom')

        assert not path.exists()
        assert not tmp_path.exists()

    def test_uses_explicit_temporary_directory(self) -> None:
        path = Path('/data/config.txt')
        tmp_dir = Path('/tmp/atomic')
        path.parent.mkdir(parents=True)
        tmp_dir.mkdir(parents=True)

        with atomic_write(path, directory=tmp_dir) as tmp_path:
            assert tmp_path.parent == tmp_dir
            tmp_path.write_text('hello')

        assert path.read_text() == 'hello'
        assert not tmp_path.exists()
        assert list(tmp_dir.iterdir()) == []


class TestDirectoryDifferencesBool:
    def test_identical_directories_are_falsy(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'a.txt', 'same')
        _write(right / 'a.txt', 'same')

        assert bool(directory_differences(left, right)) is False

    def test_empty_directories_are_falsy(self) -> None:
        left = Path('/left')
        right = Path('/right')
        left.mkdir()
        right.mkdir()

        assert bool(directory_differences(left, right)) is False

    def test_differing_directories_are_truthy(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'a.txt', 'one')
        _write(right / 'a.txt', 'two')

        assert bool(directory_differences(left, right)) is True

    def test_left_only_file_is_truthy(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'extra.txt', 'x')
        right.mkdir()

        assert bool(directory_differences(left, right)) is True


class TestDirectoryDifferencesReport:
    def test_identical_directories_report(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'a.txt', 'same')
        _write(right / 'a.txt', 'same')

        assert directory_differences(left, right).report() == 'Directories are identical'

    def test_empty_directories_report(self) -> None:
        left = Path('/left')
        right = Path('/right')
        left.mkdir()
        right.mkdir()

        assert directory_differences(left, right).report() == 'Directories are identical'

    def test_reports_file_missing_in_right(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'only_left.txt', 'x')
        right.mkdir()

        report = directory_differences(left, right).report()

        assert report == f'Missing in {right}:\n  only_left.txt'

    def test_reports_file_extra_in_right(self) -> None:
        left = Path('/left')
        right = Path('/right')
        left.mkdir()
        _write(right / 'only_right.txt', 'x')

        report = directory_differences(left, right).report()

        assert report == f'Extra in {right}:\n  only_right.txt'

    def test_reports_different_file(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'changed.txt', 'one')
        _write(right / 'changed.txt', 'two')

        report = directory_differences(left, right).report()

        assert report == 'Different files:\n  changed.txt'

    def test_reports_same_size_different_content(self) -> None:
        # shallow=False means same-size files are still compared by content
        left = Path('/left')
        right = Path('/right')
        _write(left / 'changed.txt', 'aaa')
        _write(right / 'changed.txt', 'bbb')

        report = directory_differences(left, right).report()

        assert report == 'Different files:\n  changed.txt'

    def test_reports_all_categories_together(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'gone.txt', 'x')
        _write(left / 'changed.txt', 'one')
        _write(right / 'changed.txt', 'two')
        _write(right / 'added.txt', 'y')

        report = directory_differences(left, right).report()

        assert report == (
            f'Missing in {right}:\n  gone.txt\nExtra in {right}:\n  added.txt\nDifferent files:\n  changed.txt'
        )

    def test_reports_nested_differences_with_relative_paths(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'sub' / 'deep' / 'file.txt', 'one')
        _write(right / 'sub' / 'deep' / 'file.txt', 'two')

        report = directory_differences(left, right).report()

        assert report == 'Different files:\n  sub/deep/file.txt'

    def test_reports_subdirectory_only_in_left(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'sub' / 'file.txt', 'x')
        right.mkdir()

        report = directory_differences(left, right).report()

        assert report == f'Missing in {right}:\n  sub'

    def test_report_can_be_called_multiple_times(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'changed.txt', 'one')
        _write(right / 'changed.txt', 'two')

        differences = directory_differences(left, right)

        assert differences.report() == differences.report()

    def test_report_is_unaffected_by_prior_bool_check(self) -> None:
        left = Path('/left')
        right = Path('/right')
        _write(left / 'changed.txt', 'one')
        _write(right / 'changed.txt', 'two')

        differences = directory_differences(left, right)

        assert bool(differences) is True
        assert differences.report() == 'Different files:\n  changed.txt'
