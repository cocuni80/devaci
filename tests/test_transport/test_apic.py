import pytest

from devaci.transport.apic import ApicSession


class _FakeModir:
    def __init__(self, fail_on_commit: bool = False) -> None:
        self.calls: list[str] = []
        self._fail_on_commit = fail_on_commit

    def login(self) -> None:
        self.calls.append("login")

    def commit(self, config: object) -> None:
        self.calls.append("commit")
        if self._fail_on_commit:
            raise RuntimeError("boom")

    def logout(self) -> None:
        self.calls.append("logout")


def _session() -> ApicSession:
    return ApicSession("https://apic", "u", "p", False, 10, 0, "apic")


def test_commit_logs_in_commits_and_logs_out(monkeypatch):
    monkeypatch.setattr("devaci.transport.apic.time.sleep", lambda _: None)
    session = _session()
    fake = _FakeModir()
    session._modir = fake

    session.commit(object())

    assert fake.calls == ["login", "commit", "logout"]


def test_commit_logs_out_even_when_commit_fails(monkeypatch):
    monkeypatch.setattr("devaci.transport.apic.time.sleep", lambda _: None)
    session = _session()
    fake = _FakeModir(fail_on_commit=True)
    session._modir = fake

    with pytest.raises(RuntimeError, match="boom"):
        session.commit(object())

    assert fake.calls == ["login", "commit", "logout"]
