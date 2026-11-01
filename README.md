# code-router

코드 파일을 읽어 어떤 프로그래밍 언어로 작성되었는지 판별하는 CLI입니다.
[TypeSafe AI](https://typesafe.ai) API(`typesafe-sdk`)의 `Choice` 질문을 사용해 언어를 분류하고, 선택된 언어와 신뢰도를 출력합니다.

## 요구 사항

- Python 3.15 이상 (`.python-version`에 고정)
- [uv](https://docs.astral.sh/uv/)
- TypeSafe API 키

## 설치

```
uv sync
```

프로젝트 루트에 `.env` 파일을 만들고 API 키를 넣습니다. (`.env`는 gitignore 대상입니다.)

```
TYPESAFE_API_KEY=<your-api-key>
```

## 사용법

```
uv run code-router <파일 경로>
```

예시:

```
$ uv run code-router test.file
test.file:
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}

언어: java (신뢰도 100%)
```

파일은 UTF-8로 읽습니다. API 호출이 실패하면 `언어 판별 실패: ...` 메시지를 출력하고 종료합니다.

## 판별 가능한 언어

python, javascript, typescript, java, kotlin, c, cpp, csharp, go, rust, ruby, php, swift, sql, html, css, shell, powershell, json, yaml, markdown, plaintext, other

`plaintext`는 코드가 아닌 일반 문장·자연어 텍스트입니다.
목록은 `src/code_router/__init__.py`의 `LANGUAGES`에서 수정할 수 있습니다.

## 동작 방식

1. 인자로 받은 파일을 읽어 내용을 출력합니다.
2. `TypeSafeClient.system_one()`에 코드를 `state`로, 언어 목록을 `criteria`로 갖는 `Choice` 질문을 보냅니다.
3. 가장 확률이 높은 선택지와 그 신뢰도(`confidence`)를 출력합니다.
   신뢰도가 60% 미만(`MIN_CONFIDENCE`)이면 `언어: 불확실 (가장 유력: ..., 신뢰도 ...)`로 표시합니다.
