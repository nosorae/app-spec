# 앱 기획 표준

앱의 화면, 값, 동작을 기획자와 개발자가 한 파일에 같이 적는 형식이다. 형식은 YAML 이고 문법은 `이름: 값`, 들여쓰기, `- 항목` 셋만 쓴다. 이 값이 서버, 기기 저장소, 메모리 가운데 어디에 있는지, 화면을 돌리거나 시스템이 앱을 종료한 뒤에도 남는지, 요청이 실패하면 무엇이 보이는지처럼 기획서에서 자주 빠지는 답을 형식이 대신 묻는다. 같이 들어 있는 검사 스크립트가 답이 없는 칸을 목록으로 뽑아 준다.

상태: v0.1 초안

## 한눈에 보기

화면 하나를 적으면 이렇게 된다.

```yaml
화면:
  레시피 상세:
    받는 값:
      - 레시피 id
    상태:
      레시피:
        값: 레시피 하나. 제목, 크리에이터, 저장 여부
        소스: 네트워크
        요청: GET /recipes/{레시피 id}
        갱신:
          - 화면에 들어올 때
        보관: 메모리
    컴포넌트:
      저장 버튼:
        종류: 버튼
        표시: 레시피.저장 여부
        동작:
          저장하기:
            언제: 탭
            조건: 로그인했다
            한다:
              - 요청: PUT /me/saved/{레시피 id}
                성공하면:
                  - 변경: 레시피.저장 여부
                    값: 예
                실패하면:
                  - 안내: 저장하지 못했어요
```

## 문서

- [SPEC.md](SPEC.md): 표준 본문. 규칙 일곱 개, 낱말 표, 적는 순서, 자주 나오는 것을 적는 법, 검증한 것과 한계, 빈 양식
- [examples/recipe-app.md](examples/recipe-app.md): 서버에서 받아 보여 주는 앱. 화면 7개, 백그라운드 작업 2개, 알림 1개
- [examples/running-app.md](examples/running-app.md): 기기에 저장하고 화면이 꺼져도 일이 계속되는 앱. 화면 10개, 흐름, 위젯, 미정 1건
- [docs/benchmark.md](docs/benchmark.md): 기존 형식 38개를 본 기록과 가져온 것
- [docs/platform-references.md](docs/platform-references.md): Android 와 iOS 공식 문서의 근거 문장, 낱말 대응표

처음이면 예시를 먼저 훑어서 생김새를 보고, SPEC.md 에서 규칙과 낱말을 본다.

## 검사 스크립트

Python 3 과 PyYAML 이 필요하다. 저장소 맨 위 폴더에서 돌린다.

```bash
pip install pyyaml
python3 tools/appspec_check.py examples/recipe-app.md            # 오류가 있으면 실패
python3 tools/appspec_check.py --strict examples/recipe-app.md   # 빈칸이나 미정이 있어도 실패
python3 tools/appspec_check.py --graph examples/recipe-app.md    # 화면 이동을 Mermaid 다이어그램으로 출력
python3 tools/appspec_check.py --dot examples/recipe-app.md | dot -Tpng -o 화면-이동.png   # Graphviz 가 필요하다
python3 tools/appspec_selftest.py examples/recipe-app.md         # 검사기가 위반 37가지를 잡는지 확인
```

결과는 오류, 빈칸, 미정 셋으로 나뉜다. 오류는 표준에 없는 낱말이나 없는 이름을 가리킨 것처럼 고쳐야 하는 것이고, 빈칸은 표준이 묻는데 아직 답이 없는 것, 미정은 작성자가 `미정` 에 적어 둔 것이다.

## 라이선스

MIT. [LICENSE](LICENSE) 를 본다.
