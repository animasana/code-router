import argparse

from dotenv import load_dotenv
from .lib.tools import MIN_CONFIDENCE, TypeSafeError, detect_language


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

    if confidence < MIN_CONFIDENCE:
        print(f"언어: 불확실 (가장 유력: {language}, 신뢰도 {confidence:.0%})")
    else:
        print(f"언어: {language} (신뢰도 {confidence:.0%})")
