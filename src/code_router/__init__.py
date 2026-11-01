import argparse

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient, TypeSafeError

LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "java",
    "kotlin",
    "c",
    "cpp",
    "csharp",
    "go",
    "rust",
    "ruby",
    "php",
    "swift",
    "sql",
    "html",
    "css",
    "shell",
    "powershell",
    "json",
    "yaml",
    "markdown",
    "other",
]


def detect_language(code: str) -> tuple[str, float]:
    """Jev(TypeSafe) API로 코드의 프로그래밍 언어를 판별한다."""
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"code": code},
            questions={
                "language": Choice(
                    instructions="이 코드는 어떤 프로그래밍 언어(또는 파일 형식)로 작성되었는가?",
                    criteria={lang: None for lang in LANGUAGES},
                ),
            },
        )

    answer = response.choices["language"]
    return answer.choice, answer.confidence


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Code Router CLI")

    parser.add_argument("file", help=" 코드 파일을 입력하세요")

    args = parser.parse_args()

    with open(f"{args.file}", "r", encoding="utf-8") as file:
        code = file.read()

    print(f"{args.file}:")
    print(code)

    try:
        language, confidence = detect_language(code)
    except TypeSafeError as error:
        raise SystemExit(f"언어 판별 실패: {error}") from error

    print(f"언어: {language} (신뢰도 {confidence:.0%})")
