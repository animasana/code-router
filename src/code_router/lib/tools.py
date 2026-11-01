from typesafe_sdk import Choice, TypeSafeClient

LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "java",
    "kotlin",
    "ada",
    "fortran",
    "pascal",
    "lisp",
    "prolog",
    "cobol",
    "dart",
    "objective-c",
    "perl",
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
    "plaintext",
    "other",
]


# 이름만으로 모호한 선택지에 붙이는 설명.
DESCRIPTIONS = {
    "plaintext": "프로그래밍 언어나 데이터 형식이 아닌 일반 문장·자연어 텍스트",
    "other": "위 목록에 없는 프로그래밍 언어 또는 파일 형식",
}

# 신뢰도가 이 값보다 낮으면 판별 결과를 "불확실"로 표시한다.
MIN_CONFIDENCE = 0.6


def detect_language(code: str) -> tuple[str, float]:
    """Jev(TypeSafe) API로 코드의 프로그래밍 언어를 판별한다."""
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"code": code},
            questions={
                "language": Choice(
                    instructions="이 코드는 어떤 프로그래밍 언어(또는 파일 형식)로 작성되었는가?",
                    criteria={lang: DESCRIPTIONS.get(lang) for lang in LANGUAGES},
                ),
            },
        )

    answer = response.choices["language"]
    return answer.choice, answer.confidence