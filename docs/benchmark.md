# 기존 형식 벤치마크

화면, 값이 있는 곳과 남는 기간, 동작, 화면 이동, 백그라운드 작업, 알림을 한 형식에 적는 공개 표준은 찾지 못했다. 다섯 종류 38개를 봤고 전부 일부만 겹친다. 그래서 [앱 기획 쓰는 법 v0.1](../SPEC.md) 을 새로 만들었고, 규칙과 낱말은 아래 형식들에서 가져왔다.

이 노트는 형식을 만들기 전에 기존 형식을 본 기록이다. 형식의 어느 규칙이 어디서 왔는지, 비슷한 형식에 무엇이 있었는지를 찾아볼 때 쓴다.

앱 기획 쓰는 법은 앱의 화면, 값, 동작을 기획자와 개발자가 한 파일에 YAML 로 적는 형식이다. 이 노트에 나오는 형식의 낱말은 다음과 같다.

- `화면`, `컴포넌트`: 보이는 것. 다이얼로그는 `형태` 가 다른 화면으로 적는다
- `상태`: 화면에 보이거나 판단에 쓰는 값. 그 값이 있는 곳(서버, 기기 저장소, 메모리)을 `소스` 에 적는다
- `동작`: 일어나는 일. `언제`(무엇이 시작시키는가), `조건`(무엇이 맞아야 하는가), `한다`(할 일 단계)로 적는다. 단계에는 `이동`, `실행` 같은 낱말을 쓴다
- `경우`: 조건에 따라 달라지는 모습. `로딩`, `비었음`, `오류` 는 이름이 정해져 있다
- `미정`: 아직 못 정한 것
- 검사 스크립트: 명세 파일을 읽어서 형식에 없는 낱말과 빠진 칸을 찾아 주는 프로그램

조사일은 2026-11-11 이다. 검색은 영어와 한국어로 주제마다 한 차례씩 했다. 공개돼 있는데 못 찾은 것이 있을 수 있다.

## 가장 가까운 것 다섯

형식의 목표는 화면, 컴포넌트, 값이 있는 곳과 남는 기간, 동작, 화면 이동, 백그라운드 작업, 알림을 한 형식에 적는 것이다. 빠진 것은 이 목표를 기준으로 적었다.

| 형식 | 적는 것 | 빠진 것 |
|---|---|---|
| [IFML](https://www.ifml.org/) | 화면 컨테이너, 부품, 이벤트, 이동, 값 전달 | 값이 있는 곳과 남는 기간, 백그라운드 작업, 알림. 다이어그램이 기본 표기다 |
| MD2 | 데이터, 화면, 이벤트 연결, 데이터를 가져오는 곳을 글 문법으로 | 대학 연구용 문법이다. 알림과 백그라운드 작업이 있는지는 확인하지 못했다 |
| [Event Modeling](https://eventmodeling.org/) | 화면, 명령, 사건, 조회를 시간순으로 | 화면 안의 구성, 값이 네트워크와 디스크와 메모리 가운데 어디에 있는지 |
| [Wasp](https://wasp.sh/docs/general/wasp-ts-config) | 화면, 서버 읽기와 쓰기, 백그라운드 작업, 인증을 선언 | 웹앱 전용이다. 화면 안의 상태와 남는 기간 |
| [micro-contracts 화면 스펙](https://cdn.jsdelivr.net/npm/micro-contracts@0.17.11/docs/screen-spec.md) | 화면, 이동, 이벤트를 OpenAPI 확장 필드로 | 상태가 남는 기간과 값이 있는 곳. 코드를 만드는 도구에 묶여 있다 |

## 가져온 것

### 동작을 언제, 조건, 한다로 나누기

서로 다른 세 곳이 같은 세 칸을 쓴다.

집 안 기기를 자동으로 움직이는 설정인 Home Assistant 자동화 ([Understanding automations](https://www.home-assistant.io/docs/automation/basics/))

> A trigger is the part of an automation that makes the automation start when something specific happens ...
>
> Conditions check whether something is true at that moment ...
>
> An action makes Home Assistant do something ...

요구사항을 정해진 문장 틀로 쓰는 방법인 EARS ([alistairmavin.com/ears](https://alistairmavin.com/ears/))

> When <trigger>, the <system name> shall <system response>
>
> While <precondition(s)>, the <system name> shall <system response>

테스트 시나리오를 쓰는 문법인 Gherkin ([Gherkin Reference](https://cucumber.io/docs/gherkin/reference/))

> Given steps are used to describe the initial context of the system - the scene of the scenario.
>
> When steps are used to describe an event, or an action.
>
> Then steps are used to describe an expected outcome, or result.

풀이. 집 자동화 설정, 요구사항 문장 틀, 테스트 시나리오 문법이 모두 "무엇이 시작시키는가, 그때 무엇이 맞아야 하는가, 무엇을 하는가" 셋으로 나눈다. 형식의 `언제`, `조건`, `한다` 가 이 셋이다. 버튼 탭, 화면 진입, 알림 탭, 백그라운드 작업을 한 모양으로 적는 것도 Home Assistant 가 모든 자동화를 이 세 칸으로 적는 데서 가져왔다.

### 화면, 컴포넌트, 이동

Shape Up 의 breadboarding ([Shape Up 4장](https://basecamp.com/shapeup/1.3-chapter-04))

> These are things you can navigate to, like screens, dialogs, or menus that pop up.
>
> These are things the user can act on, like buttons and fields.
>
> These show how the affordances take the user from place to place.

풀이. 차례로 places, affordances, connection lines 의 정의다. 형식의 `화면`, `컴포넌트`, `이동` 에 해당한다. 다이얼로그와 팝업 메뉴도 place 로 치는 것을 따라서 형식도 다이얼로그와 바텀시트를 `형태` 가 다른 화면으로 적는다.

### 로딩, 비었음, 오류

Scott Hurff 의 UI Stack ([글](https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/))은 화면 하나에 상태 다섯을 빠짐없이 설계하라고 한다. 글의 절 제목이 Ideal State, Empty State, Error State, Partial State, Loading State 다.

풀이. 형식은 이 가운데 셋에 정해진 이름(`로딩`, `비었음`, `오류`)을 주고 `경우` 에 적게 했다. Ideal 은 컴포넌트 본문이고, Partial 은 문장 조건으로 적는다. 서버에서 받는 값을 보여 주는 컴포넌트에 `로딩` 과 `오류` 가 없으면 검사가 빈칸으로 알린다.

### 한 번 적고 이름으로 가리키기

OpenAPI 3.1 ([명세](https://spec.openapis.org/oas/v3.1.0.html))

> Holds a set of reusable objects for different aspects of the OAS.
>
> A simple object to allow referencing other components in the OpenAPI document, internally and externally.

GitHub Actions ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax))

> Selects an action to run as part of a step in your job.

풀이. 첫째와 둘째는 OpenAPI 의 Components Object 와 Reference Object 설명이고, 셋째는 GitHub Actions 의 `uses` 설명이다. 다시 쓸 것을 한 곳에 적어 두고 다른 곳에서는 가리키기만 한다. 형식은 서버와 저장소를 `소스` 에, 여러 화면이 쓰는 값을 맨 위 `상태` 에, 여러 곳에서 하는 일을 맨 위 `동작` 에 한 번 적고 이름으로 가리킨다. `실행` 단계가 `uses` 에 해당한다. 서버 응답의 필드를 형식에 다시 적지 않고 API 문서 링크만 거는 것도 같은 생각이다.

### YAML 에서 쓰는 문법 줄이기

YAML 1.2.2 명세 ([7.3.3 Plain Style](https://yaml.org/spec/1.2.2/))

> Plain scalars must never contain the “: ” and “ #” character combinations.

풀이. 따옴표 없이 쓴 값 안에는 콜론 뒤 빈칸과 빈칸 뒤 샵이 올 수 없다. 형식의 따옴표 규칙(값 안에 콜론 뒤 빈칸이나 빈칸 뒤 샵이 있으면 큰따옴표로 감싼다)이 여기서 나왔다.

YAML 1.1 의 참거짓 값 ([Boolean Language-Independent Type](https://yaml.org/type/bool.html))은 정규식이 `y|Y|yes|Yes|YES|n|N|no|No|NO` 로 시작한다.

풀이. YAML 1.1 을 따르는 파서는 `yes`, `no` 를 글자가 아니라 참거짓으로 읽는다. 형식이 값으로 `예`, `아니오` 를 쓰고 모든 값을 글자로 읽는다고 정한 이유다.

StrictYAML ([What YAML features does StrictYAML remove?](https://hitchdev.com/strictyaml/features-removed/))

> StrictYAML restricts you from parsing a number of things which the YAML specification says should be parsed.

같은 페이지가 뺀 기능으로 Implicit Typing, Duplicate Keys Disallowed, Node anchors and refs, Flow style, Explicit tags 를 든다. 같은 키를 두 번 썼을 때를 다룬 페이지([Duplicate keys disallowed](https://hitchdev.com/strictyaml/why/duplicate-keys-disallowed/))는 이렇게 쓴다.

> Duplicate keys are allowed in regular YAML - as parsed by pyyaml, ruamel.yaml and poyo ...

풀이. StrictYAML 은 YAML 을 읽을 때 놀랄 일을 줄이려고 다섯 가지를 뺐다. 자동 형 변환(`yes` 를 참으로 읽는 것 같은 일), 같은 키 두 번, 앵커(값에 이름을 붙여 두고 다른 곳에서 다시 쓰는 기능), 대괄호와 중괄호 묶음, 태그(값의 형을 지정하는 표시)다. 형식도 같은 다섯을 쓰지 않고, 검사 스크립트가 쓰인 곳을 오류로 알린다. 일반 YAML 파서는 같은 키가 두 번 나와도 그냥 읽기 때문에 검사 스크립트가 따로 잡는다. StrictYAML 은 개인이 만든 파이썬 파서이고 YAML 공식 명세가 아니다.

Maestro ([Maestro Flows](https://docs.maestro.dev/maestro-flows))

> ... human-readable YAML format designed to be maintained by both developers and manual testers ...

풀이. 모바일 UI 테스트 도구 Maestro 는 개발자와 수동 테스터가 같이 고치는 YAML 을 목표로 내세운다. 개발자가 아닌 사람이 YAML 을 고치는 선례다. 실제로 그렇게 쓰이는지를 보여 주는 숫자는 그 문서에 없다.

### 못 정한 것을 표시하기

GitHub Spec Kit 의 명세 템플릿([spec-template.md](https://raw.githubusercontent.com/github/spec-kit/main/templates/spec-template.md))은 모르는 것을 추측으로 채우지 말고 `NEEDS CLARIFICATION` 표시를 남기게 한다.

풀이. 형식의 `미정` 이 같은 역할이다. 빈칸으로 두면 잊은 것인지 못 정한 것인지 알 수 없어서, 못 정한 것은 무엇을 정해야 하는지를 문장으로 적게 했다.

## 따라 하지 않은 것

Martin Fowler 사이트의 Spec Kit, Kiro 사용 후기 ([Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

> spec-kit created a LOT of markdown files for me to review.
>
> They were repetitive, both with each other, and with the code that already existed.

풀이. 기능 하나에 문서가 여러 개 생기고 내용이 겹쳐서 검토가 부담이었다는 지적이다. 같은 글은 Kiro 의 작업 순서를 작은 버그 수정에 썼을 때를 "like using a sledgehammer to crack a nut" 라고 적었다. 형식이 문서 종류를 나누지 않고 한 형식, 짧은 낱말로 간 이유다.

CAMELEON 참조 프레임워크 ([W3C 커뮤니티 위키](https://www.w3.org/community/uad/wiki/Cameleon_Reference_Framework))

> At the time of writing the Cameleon Reference Framework has only been implemented in research tools such as UsiXML and MARIA.

풀이. 화면을 과제, 추상 UI, 구체 UI, 최종 UI 네 단계 모델로 나누는 틀인데, 이 글을 쓴 때에는 연구 도구로만 구현됐다고 한다. 모델을 여러 벌 두는 방식은 따라 하지 않았다.

Power Apps 소스 YAML ([Power Apps YAML](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml)) 페이지는 이 YAML 이 "read-only and can't be modified" 라고 적는다.

풀이. 화면과 컨트롤을 YAML 로 적는 가장 큰 사례다. 다만 사람이 쓰는 명세로 만든 것은 아니고, 도구가 내보내는 결과물이다.

IFML 은 2013년 3월에 소프트웨어 표준 단체 OMG 의 표준이 됐다(["IFML has been adopted as a standard by OMG in March 2013."](https://www.ifml.org/)). 화면 컨테이너, 부품, 이벤트, 이동과 값 전달을 나눈 구성은 형식과 가장 닮았다. 다만 다이어그램이 기본 표기이고 파일로 주고받는 형식은 XML 의 한 종류인 XMI 라서, 글로 손쉽게 쓰는 형식이라는 목표와 맞지 않았다.

## 본 형식 38개

빠진 것은 형식의 목표(화면, 컴포넌트, 값이 있는 곳과 남는 기간, 동작, 이동, 백그라운드 작업, 알림을 한 형식에) 기준이고, 열어 본 문서에 없었다는 뜻이다.

### AI 코딩 도구용 명세 6개

| 형식 | 적는 것 | 빠진 것 |
|---|---|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit) | 기능마다 명세, 계획, 작업 목록 문서. 사용자 시나리오, 기능 요구사항, 성공 기준 | 화면과 상태를 적는 칸. 저장소는 계획 문서의 `Storage` 한 줄이다 |
| [Kiro specs](https://kiro.dev/docs/specs/feature-specs/) | 요구사항, 설계, 작업 세 문서. 요구사항은 `WHEN [condition/event] THE SYSTEM SHALL [expected behavior]` 문장 | 화면과 상태의 구조 |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 요구사항과 시나리오를 마크다운 제목으로. 바뀌는 부분을 따로 적는다 | 화면, 상태, 값이 있는 곳 |
| BMAD-METHOD | 제품 요구사항 문서(PRD)와 아키텍처 문서 템플릿 | 옛 판(4.35) 템플릿만 봤다. 화면은 목록 수준이었다 |
| Tessl | 코드 파일마다 명세 파일을 두고 대상 코드를 `targets` 로 가리킨다 | 화면 단위 구조 |
| [AGENTS.md](https://agents.md) | 코딩 에이전트에게 주는 작업 지침. 정해진 칸이 없다 | 앱 명세가 아니다 |

### 화면과 상호작용 모델 6개

| 형식 | 적는 것 | 빠진 것 |
|---|---|---|
| [IFML](https://www.ifml.org/) | 화면 컨테이너, 부품, 이벤트, 이동, 값 전달 | 값이 있는 곳, 백그라운드 작업, 알림 |
| CAMELEON 과 UsiXML ([W3C MBUI 소개](https://www.w3.org/TR/mbui-intro/)) | 과제에서 최종 UI 까지 네 단계 모델 | 연구 도구로만 구현됐다 |
| [SCXML](https://www.w3.org/TR/scxml/) | 상태, 전이, 이벤트, 조건 | 화면 구성, 값이 있는 곳 |
| [XState](https://stately.ai/docs/states) | 상태 기계를 겹친 객체로 | 화면 구성, 값이 있는 곳. 자바스크립트 코드다 |
| MD2 | 데이터, 화면, 이벤트 연결, 데이터를 가져오는 곳 | 연구용 문법 |
| MAML | 데이터, 화면, 로직을 다이어그램으로 | 글 형식이 없다 |

### 기획 표기법 9개

| 형식 | 적는 것 | 빠진 것 |
|---|---|---|
| [Shape Up breadboarding](https://basecamp.com/shapeup/1.3-chapter-04) | 갈 수 있는 곳, 누를 수 있는 것, 둘을 잇는 선 | 값, 상태, 백그라운드 작업 |
| [UI flow shorthand](https://signalvnoise.com/posts/1926-a-shorthand-for-designing-ui-flows) | 보이는 것을 선 위에, 하는 것을 선 아래에 | 값, 상태, 백그라운드 작업 |
| [Event Modeling](https://eventmodeling.org/) | 화면, 명령, 사건, 조회를 시간순으로 | 화면 안의 구성, 값이 있는 곳의 구분 |
| [OOUX](https://ooux.com/offerings/xrayux) | 객체, 관계, 행동, 속성 | 값이 있는 곳, 시간 순서 |
| [UI Stack](https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/) | 화면의 상태 다섯 | 상태가 바뀌는 조건, 값이 있는 곳 |
| [User Story Mapping](https://www.jpattonassociates.com/the-new-backlog/) | 활동, 과제, 스토리 | 화면 안, 값 |
| [EARS](https://alistairmavin.com/ears/) | 요구사항 문장 틀 다섯 | 화면 구조. 문장 하나 단위다 |
| [Gherkin](https://cucumber.io/docs/gherkin/reference/) | Given, When, Then 시나리오 | 화면 구조. 예마다 상황을 처음부터 적는다 |
| 국내 화면설계서 ([IT위키 스토리보드](https://www.itwiki.kr/w/%EC%8A%A4%ED%86%A0%EB%A6%AC%EB%B3%B4%EB%93%9C), [요즘IT](https://yozm.wishket.com/magazine/detail/1112)) | 화면 ID, 화면명, 화면 설명, 기능 설명, 흐름, 정책과 예외 | 칸만 있고 적는 규칙이 없다. 값이 남는 기간과 백그라운드 작업 칸은 본 글 세 곳에 없었다 |

### 앱을 선언으로 적는 형식과 문서 표준 11개

| 형식 | 적는 것 | 빠진 것 |
|---|---|---|
| [Wasp](https://wasp.sh/docs/general/wasp-ts-config) | 화면, 서버 읽기와 쓰기, 백그라운드 작업, 인증 | 웹앱 전용. 화면 안의 상태 |
| [Power Apps 소스 YAML](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml) | 화면, 컨트롤, 속성 | 도구가 내보내는 읽기 전용 파일 |
| [FlutterFlow 프로젝트 YAML](https://docs.flutterflow.io/resources/projects/settings/project-apis) | 프로젝트 전체 구조 | FlutterFlow 전용 |
| [JHipster JDL](https://www.jhipster.tech/jdl/entities-fields) | 데이터 모델과 앱 설정 | 화면과 동작 |
| [Adaptive Cards](https://learn.microsoft.com/en-us/adaptive-cards/authoring-cards/getting-started) | 카드 한 장의 요소와 동작 | 앱 전체 구조 |
| [DivKit](https://divkit.tech/doc/) | 서버가 내려 주는 화면 조각 | 앱 전체 구조 |
| [A2UI](https://github.com/google/A2UI) | 에이전트가 내려 주는 화면 조각 | 앱 전체 구조 |
| [micro-contracts 화면 스펙](https://cdn.jsdelivr.net/npm/micro-contracts@0.17.11/docs/screen-spec.md) | 화면, 이동, 이벤트 | 상태가 남는 기간, 값이 있는 곳 |
| [Melody](https://github.com/josejuanqm/melody) | YAML 과 Lua 로 적은 화면을 SwiftUI 와 Compose 로 실행 | 앱을 실행하는 틀이라 명세로 쓰는 것과 목적이 다르다 |
| ISO/IEC/IEEE 29148 (요구사항 공학 국제 표준) | 요구사항 명세서의 목차 | 화면 단위 구조. 본문은 유료라 비공식 사본의 목차만 봤다 |
| [arc42](https://arc42.org/overview) | 아키텍처 문서 12절 | 화면 단위 구조 |

### 설정 형식 6개

앱 명세는 아니고, 적은 규칙으로 복잡한 것을 조립하는 방법을 보려고 봤다.

| 형식 | 되풀이되는 모양 | 가져온 것 |
|---|---|---|
| [Home Assistant 자동화](https://www.home-assistant.io/docs/automation/basics/) | triggers, conditions, actions | 동작의 세 칸 |
| [GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) | on, jobs, steps | 단계 목록, `uses` 로 다시 쓰기 |
| [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html) | paths, components | 한 번 적고 가리키기 |
| [Maestro](https://docs.maestro.dev/maestro-flows) | 명령 목록 | 단계를 `낱말: 대상` 한 줄로 |
| [Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/) | apiVersion, kind, metadata, spec | 모든 블록이 같은 바깥 모양 |
| [StrictYAML](https://hitchdev.com/strictyaml/features-removed/) | YAML 에서 뺀 기능 | 문법 줄이기 |

## 확인하지 못한 것

- Airbnb 의 서버 주도 UI(Ghost Platform) 글은 접근이 막혀 열지 못했다. 섹션, 화면, 액션으로 나눈다는 것은 검색 결과 요약으로만 봤다
- IFML 스펙과 MD2 논문은 PDF 라서 인용문을 원문과 글자 단위로 대조하지 못했다. 그래서 위에 인용하지 않았다
- Material Design 과 Apple HIG 의 빈 상태, 로딩, 오류 지침은 페이지 본문을 받지 못했다
- BMAD-METHOD 는 4.35 판 템플릿만 봤다. 현재 판의 구조는 보지 않았다
- 각 형식이 실무에서 얼마나 쓰이는지는 조사하지 않았다
- 한국어로 공개된 화면 명세 YAML 표준은 검색에서 나오지 않았다. 사내 문서로만 있는 것은 알 수 없다

## 참고 자료

인용문은 원문 페이지에 그 문장이 있는지 스크립트로 확인했다(2026-11-11). 플랫폼 공식 문서의 근거는 [2026-11-11-플랫폼-공식-근거](platform-references.md) 에 따로 모았다.

- Home Assistant, Understanding automations: https://www.home-assistant.io/docs/automation/basics/
- EARS: https://alistairmavin.com/ears/
- Gherkin Reference: https://cucumber.io/docs/gherkin/reference/
- Shape Up 4장 Breadboarding: https://basecamp.com/shapeup/1.3-chapter-04
- UI Stack: https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/
- OpenAPI 3.1.0: https://spec.openapis.org/oas/v3.1.0.html
- GitHub Actions Workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- YAML 1.2.2: https://yaml.org/spec/1.2.2/
- YAML 1.1 Boolean: https://yaml.org/type/bool.html
- StrictYAML: https://hitchdev.com/strictyaml/features-removed/
- Maestro Flows: https://docs.maestro.dev/maestro-flows
- GitHub Spec Kit: https://github.com/github/spec-kit
- Martin Fowler 사이트의 SDD 도구 후기: https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- CAMELEON 참조 프레임워크: https://www.w3.org/community/uad/wiki/Cameleon_Reference_Framework
- Power Apps YAML: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/power-apps-yaml
- IFML: https://www.ifml.org/
