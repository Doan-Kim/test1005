커맨드 플러그인 사용법

- 새로운 커맨드를 추가하려면 `cli/commands/` 폴더에 모듈(.py)을 추가하세요.
- 각 모듈은 `commands`라는 dict를 내보내야 합니다.
  - 키: 커맨드 이름(문자열)
  - 값: 함수(callable)로 시그니처는 `(cli_instance, arg)`입니다.

예시:

```py
def mycmd(cli, arg):
    # do something
    pass

commands = {
    'mycmd': mycmd,
}
```

앱 진입점은 `cli/app.py`입니다. 실행 시 자동으로 `cli.commands` 하위 모듈을 찾아 바인딩합니다.
