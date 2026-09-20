from __future__ import annotations

from batocera_launch.emulators.opengoal import _merge_pc_settings

# as the game writes it: managed keys, keys only it knows, and a nested block of player progress
_EXISTING = """(settings #x1000A00040000
  (fps 60)
  (msaa 1)
  (aspect-state aspect4x3 4 3 #t)
  (vsync #t)
  (stick-deadzone 0.3)
  (secrets
    (hard-rats? #f)
    (hard-rats-hiscore 1234)
    (music
      (test-track 1)
      )
    )
  (memcard-vibration? #t)
  )
"""


class TestMergePcSettings:
    def test_writes_a_fresh_file_when_there_is_nothing_to_merge(self) -> None:
        result = _merge_pc_settings('', 0x1000A00040000, {'fps': '60', 'vsync': '#t'})

        assert result == '(settings #x1000a00040000\n  (fps 60)\n  (vsync #t)\n  )\n'

    def test_replaces_managed_keys_in_place(self) -> None:
        result = _merge_pc_settings(_EXISTING, 0x1000A00040000, {'fps': '150', 'vsync': '#f'})

        assert '(fps 150)' in result
        assert '(fps 60)' not in result
        assert '(vsync #f)' in result

    def test_preserves_unmanaged_keys(self) -> None:
        result = _merge_pc_settings(_EXISTING, 0x1000A00040000, {'fps': '150'})

        assert '(stick-deadzone 0.3)' in result
        assert '(memcard-vibration? #t)' in result

    def test_preserves_nested_blocks_verbatim(self) -> None:
        result = _merge_pc_settings(_EXISTING, 0x1000A00040000, {'fps': '150'})

        assert '(hard-rats-hiscore 1234)' in result
        assert '(test-track 1)' in result
        assert result.count('(secrets') == 1

    def test_does_not_reach_into_nested_blocks(self) -> None:
        result = _merge_pc_settings(_EXISTING, 0x1000A00040000, {'hard-rats?': '#t'})

        assert '(hard-rats? #f)' in result
        # appended at the top level rather than replacing the one inside (secrets ...)
        assert result.count('(hard-rats? #t)') == 1

    def test_appends_managed_keys_the_file_does_not_have_yet(self) -> None:
        result = _merge_pc_settings(_EXISTING, 0x1000A00040000, {'speedrunner-mode?': '#f'})

        assert '(speedrunner-mode? #f)' in result

    def test_rewrites_the_version_header(self) -> None:
        result = _merge_pc_settings(_EXISTING, 0x20000, {})

        assert result.startswith('(settings #x20000\n')

    def test_keeps_a_valueless_form(self) -> None:
        result = _merge_pc_settings('(settings #x20000\n  (panic)\n  )\n', 0x20000, {})

        assert '(panic)' in result
