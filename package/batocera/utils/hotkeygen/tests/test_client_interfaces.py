from __future__ import annotations

from hotkeygen.dbus._generate_client_interfaces import CLIENT_INTERFACES_FILE, generate_client_interfaces


def test_client_interafaces_matches() -> None:
    assert CLIENT_INTERFACES_FILE.read_text() == generate_client_interfaces(), 'Regenerate the client interfaces'
