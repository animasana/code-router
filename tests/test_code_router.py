"""code_router 테스트. 실제 TypeSafe API는 호출하지 않고 클라이언트를 가짜로 대체한다."""

from types import SimpleNamespace

import pytest
from typesafe_sdk import TypeSafeError

import code_router
from code_router.lib import tools


class FakeClient:
    """`TypeSafeClient`를 대신하는 가짜 클라이언트. 호출 인자를 기록한다."""

    def __init__(self, choice: str, confidence: float):
        self._answer = SimpleNamespace(choice=choice, confidence=confidence)
        self.calls: list[dict] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def system_one(self, state, questions, **kwargs):
        self.calls.append({"state": state, "questions": questions, **kwargs})
        return SimpleNamespace(choices={"language": self._answer})


@pytest.fixture
def fake_client(monkeypatch):
    """`tools.TypeSafeClient()`가 가짜 클라이언트를 반환하도록 패치한다."""

    def install(choice: str = "python", confidence: float = 0.99) -> FakeClient:
        client = FakeClient(choice, confidence)
        monkeypatch.setattr(tools, "TypeSafeClient", lambda: client)
        return client

    return install


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch):
    """테스트가 실제 .env를 읽지 않도록 한다."""
    monkeypatch.setattr(code_router, "load_dotenv", lambda: None)


def run_main(monkeypatch, path) -> None:
    monkeypatch.setattr("sys.argv", ["code-router", str(path)])
    code_router.main()


# --- 후보 목록 ---


def test_languages_are_unique():
    assert len(tools.LANGUAGES) == len(set(tools.LANGUAGES))


def test_languages_include_fallback_labels():
    # 코드가 아닌 입력이 엉뚱한 언어로 분류되지 않도록 폴백 라벨이 필요하다.
    assert "plaintext" in tools.LANGUAGES
    assert "other" in tools.LANGUAGES


def test_descriptions_refer_to_known_languages():
    assert set(tools.DESCRIPTIONS) <= set(tools.LANGUAGES)


# --- detect_language ---


def test_detect_language_returns_choice_and_confidence(fake_client):
    fake_client("rust", 0.97)

    assert tools.detect_language("fn main() {}") == ("rust", 0.97)


def test_detect_language_sends_code_and_choice_question(fake_client):
    client = fake_client()

    tools.detect_language("print('hi')")

    (call,) = client.calls
    assert call["state"] == {"code": "print('hi')"}
    question = call["questions"]["language"]
    assert question.type == "choice"
    assert list(question.criteria) == tools.LANGUAGES
    assert question.criteria["plaintext"] == tools.DESCRIPTIONS["plaintext"]
    assert question.criteria["python"] is None


# --- main ---


def test_main_prints_file_and_language(fake_client, monkeypatch, tmp_path, capsys):
    fake_client("java", 1.0)
    source = tmp_path / "Main.java"
    source.write_text("class Main {}", encoding="utf-8")

    run_main(monkeypatch, source)

    out = capsys.readouterr().out
    assert f"{source}:" in out
    assert "class Main {}" in out
    assert "언어: java (신뢰도 100%)" in out


def test_main_reports_uncertain_below_threshold(fake_client, monkeypatch, tmp_path, capsys):
    fake_client("json", 0.56)
    source = tmp_path / "note.txt"
    source.write_text("안녕하세요", encoding="utf-8")

    run_main(monkeypatch, source)

    out = capsys.readouterr().out
    assert "언어: 불확실 (가장 유력: json, 신뢰도 56%)" in out


def test_main_accepts_exactly_min_confidence(fake_client, monkeypatch, tmp_path, capsys):
    fake_client("go", tools.MIN_CONFIDENCE)
    source = tmp_path / "main.go"
    source.write_text("package main", encoding="utf-8")

    run_main(monkeypatch, source)

    out = capsys.readouterr().out
    assert "불확실" not in out
    assert "언어: go" in out


def test_main_exits_with_message_on_api_error(monkeypatch, tmp_path):
    class FailingClient(FakeClient):
        def system_one(self, *args, **kwargs):
            raise TypeSafeError("boom")

    monkeypatch.setattr(tools, "TypeSafeClient", lambda: FailingClient("x", 0))
    source = tmp_path / "a.py"
    source.write_text("pass", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        run_main(monkeypatch, source)

    assert "언어 판별 실패" in str(exc.value)
    assert "boom" in str(exc.value)


def test_main_missing_file_raises(fake_client, monkeypatch, tmp_path):
    fake_client()

    with pytest.raises(FileNotFoundError):
        run_main(monkeypatch, tmp_path / "nope.py")
