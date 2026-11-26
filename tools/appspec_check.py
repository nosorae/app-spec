#!/usr/bin/env python3
"""앱 기획 표준 v0.1 검사기.

쓰는 법
  python3 appspec_check.py 명세.yaml              파일 하나
  python3 appspec_check.py 명세폴더/               폴더 안 파일을 합쳐 한 명세로 본다
  python3 appspec_check.py --strict 명세폴더/      빈칸과 미정도 실패로 본다 (개발 착수 기준)
  python3 appspec_check.py --graph 명세폴더/       화면 이동을 Mermaid 로 찍는다
  python3 appspec_check.py --dot 명세폴더/ | dot -Tpng -o 화면-이동.png
                                                   화면 이동을 이미지로 만든다 (Graphviz 가 필요하다)

.yaml, .yml 은 파일 전체를 읽고 .md 는 ```yaml 블록만 읽는다.
결과는 셋으로 나눠 찍는다.
  오류  표준에 없는 낱말, 없는 이름을 가리킴, 같은 이름이 두 번
  빈칸  표준이 묻는 질문에 아직 답이 없음
  미정  작성자가 `미정`으로 적어 둔 것
PyYAML 이 필요하다 (pip install pyyaml).
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML 이 필요하다: pip install pyyaml")

TOP = ["앱", "소스", "상태", "동작", "흐름", "화면", "백그라운드 작업", "알림"]
COMMON = ["설명", "미정"]
APP = ["이름", "시작 화면", "탭", "기본"]
APP_DEFAULT = ["경우", "요청 실패"]
SOURCE = ["네트워크", "디스크"]
SERVER = ["주소", "인증", "문서"]
DISK = ["종류"]
DISK_KINDS = ["디비", "설정", "파일", "보안 저장소"]
STATE_COMMON = ["값", "소스", "비움"]
STATE_BY_KIND = {
    "네트워크": (["요청", "갱신", "보관"], ["서버"]),
    "디스크": (["저장소"], []),
    "메모리": (["구성 변경에도 유지", "프로세스 종료에도 유지"], []),
    "기기": (["기능"], []),
    "계산": (["식"], []),
}
STATE_QUESTION = {
    "값": "어떤 값인지 `값`에 적는다",
    "소스": "값이 실제로 어디에 있는지 `소스`에 적는다 (네트워크, 디스크, 메모리, 기기, 계산)",
    "요청": "서버에 무엇을 요청해 받는 값인지 `요청`에 적는다",
    "갱신": "언제 서버에서 다시 받는지 `갱신`에 적는다",
    "보관": "받은 값을 기기 어디에 보관하는지 `보관`에 적는다 (없음, 메모리, 디스크 저장소 이름)",
    "저장소": "어느 디스크 저장소에 두는지 `저장소`에 적는다",
    "구성 변경에도 유지": "화면 회전 같은 구성 변경 뒤에도 값이 남아야 하는지 `구성 변경에도 유지`에 예, 아니오로 적는다",
    "프로세스 종료에도 유지": "백그라운드에서 시스템이 프로세스를 종료한 뒤 돌아와도 값이 남아야 하는지 `프로세스 종료에도 유지`에 예, 아니오로 적는다",
    "기능": "기기의 어떤 기능이 주는 값인지 `기능`에 적는다",
    "식": "어떤 상태로 어떻게 계산하는지 `식`에 적는다",
}
ACTION = ["언제", "조건", "한다", "겹치면"]
VERBS = ["이동", "요청", "변경", "새로고침", "안내", "알림", "예약", "취소", "분석", "기기", "실행"]
STEP_OPTS = {
    "이동": ["넘기는 값", "방식"],
    "요청": ["서버", "성공하면", "실패하면"],
    "변경": ["값"],
    "새로고침": [],
    "안내": [],
    "알림": ["넘기는 값"],
    "예약": ["언제", "넘기는 값"],
    "취소": ["넘기는 값"],
    "분석": [],
    "기기": ["성공하면", "실패하면"],
    "실행": [],
}
NAV_MODES = ["쌓기", "바꾸기", "비우고 이동"]
FLOW = ["화면", "상태", "동작"]
SCREEN = ["형태", "받는 값", "링크", "디자인", "상태", "동작", "컴포넌트"]
SCREEN_FORMS = ["전체 화면", "다이얼로그", "바텀시트", "위젯"]
COMPONENT = ["종류", "문구", "표시", "경우", "상태", "동작", "컴포넌트"]
CASE_BODY = ["문구", "표시", "동작", "컴포넌트"]
STD_CASES = ["로딩", "비었음", "오류"]
JOB = ["언제", "미뤄도 됨", "조건", "한다", "다시 시도", "겹치면", "진행 알림", "받는 값"]
JOB_OVERLAP = ["건너뜀", "바꿈", "줄 세움"]
NOTI = ["보내는 곳", "받는 값", "분류", "중요도", "제목", "본문", "앱을 보고 있을 때", "동작"]
NOTI_FROM = ["서버", "앱"]
NOTI_LEVEL = ["높음", "보통", "낮음"]
YES_NO = ["예", "아니오"]

QUOTE_HINT = (
    " 값이 [ { \" ' * & ! | > % @ ` 로 시작하거나 값 안에 콜론 뒤 빈칸(: )이나"
    " 빈칸 뒤 샵( #)이 있으면 따옴표로 감싼다."
)


class S(str):
    pos = None


class L(list):
    pos = None


class M(dict):
    pos = None

    def __init__(self):
        super().__init__()
        self.keypos = {}


class Report:
    def __init__(self):
        self.items = {"오류": [], "빈칸": [], "미정": []}

    def add(self, level, pos, path, msg):
        self.items[level].append((pos, " > ".join(path), msg))

    def error(self, pos, path, msg):
        self.add("오류", pos, path, msg)

    def blank(self, pos, path, msg):
        self.add("빈칸", pos, path, msg)


def josa(word, pair):
    """받침에 맞는 조사를 고른다. pair 는 '받침 있을 때/없을 때' 순서다 (을/를, 이/가, 은/는, 으로/로)."""
    with_final, without_final = pair.split("/")
    last = str(word).rstrip()[-1:]
    if "가" <= last <= "힣":
        final = (ord(last) - 0xAC00) % 28
        if pair == "으로/로" and final == 8:
            return without_final
        return with_final if final else without_final
    return without_final


def suggest(word, candidates):
    squeezed = word.replace(" ", "")
    for cand in candidates:
        if cand.replace(" ", "") == squeezed:
            return f" `{cand}` {josa(cand, '으로/로')} 적는다."
    close = difflib.get_close_matches(word, list(candidates), n=1, cutoff=0.6)
    return f" 혹시 `{close[0]}`?" if close else ""


# ---------------------------------------------------------------- 읽기

BANNED_TOKENS = [
    (yaml.tokens.AnchorToken, "앵커(&)"),
    (yaml.tokens.AliasToken, "별칭(*)"),
    (yaml.tokens.TagToken, "태그(!)"),
    (yaml.tokens.FlowMappingStartToken, "중괄호 묶음({ })"),
    (yaml.tokens.FlowSequenceStartToken, "대괄호 묶음([ ])"),
]


def convert(node, file, offset, rep):
    pos = (file, node.start_mark.line + offset + 1)
    if isinstance(node, yaml.ScalarNode):
        value = S(node.value.strip())
        value.pos = pos
        return value
    if isinstance(node, yaml.SequenceNode):
        items = L(convert(child, file, offset, rep) for child in node.value)
        items.pos = pos
        return items
    mapping = M()
    mapping.pos = pos
    for key_node, value_node in node.value:
        key_pos = (file, key_node.start_mark.line + offset + 1)
        if not isinstance(key_node, yaml.ScalarNode):
            rep.error(key_pos, [], "이름은 글자로 적는다")
            continue
        key = key_node.value.strip()
        if key in mapping:
            rep.error(key_pos, [], f"`{key}` {josa(key, '이/가')} 같은 곳에 두 번 나온다")
            continue
        mapping[key] = convert(value_node, file, offset, rep)
        mapping.keypos[key] = key_pos
    return mapping


def load_text(text, file, offset, rep):
    try:
        for token in yaml.scan(text, Loader=yaml.BaseLoader):
            line = token.start_mark.line + offset + 1
            for cls, name in BANNED_TOKENS:
                if isinstance(token, cls):
                    rep.error(
                        (file, line),
                        [],
                        f"{name}은 이 표준에서 쓰지 않는다. 목록은 줄마다 `- ` 로 적고, 값이 그 기호로 시작하면 따옴표로 감싼다",
                    )
            if isinstance(token, yaml.tokens.ScalarToken) and token.style in ("|", ">"):
                rep.error((file, line), [], "여러 줄 글자(| 나 >)는 쓰지 않는다. 문장 목록으로 적는다")
        loader = yaml.BaseLoader(text)
        try:
            node = loader.get_single_node()
        finally:
            loader.dispose()
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = (mark.line if mark else 0) + offset + 1
        problem = getattr(exc, "problem", None) or str(exc)
        rep.error((file, line), [], f"YAML 로 읽을 수 없다 ({problem}).{QUOTE_HINT}")
        return None
    if node is None:
        return M()
    root = convert(node, file, offset, rep)
    if not isinstance(root, M):
        rep.error(root.pos, [], "맨 위에는 `앱:`, `화면:` 같은 블록 이름이 와야 한다")
        return None
    return root


def read_blocks(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        return [(text, 0)]
    blocks = []
    for match in re.finditer(r"^```ya?ml[ \t]*\n(.*?)^```", text, re.M | re.S):
        offset = text.count("\n", 0, match.start(1))
        blocks.append((match.group(1), offset))
    return blocks


def collect_files(paths):
    files = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files += sorted(p for p in path.rglob("*") if p.suffix.lower() in (".yaml", ".yml", ".md"))
        elif path.exists():
            files.append(path)
        else:
            sys.exit(f"파일이 없다: {raw}")
    return files


def merge_named(base, add, section, rep):
    for name, value in add.items():
        if name in base:
            rep.error(add.keypos[name], [section], f"`{name}` {josa(name, '이/가')} 다른 곳에도 정의돼 있다")
            continue
        base[name] = value
        base.keypos[name] = add.keypos[name]


def merge(spec, part, rep):
    for key, value in part.items():
        if key not in spec:
            spec[key] = value
            spec.keypos[key] = part.keypos[key]
            continue
        if key == "앱":
            rep.error(part.keypos[key], [], "`앱` 블록은 한 번만 적는다")
        elif not isinstance(value, M) or not isinstance(spec[key], M):
            rep.error(part.keypos[key], [key], "`이름:` 으로 시작하는 줄이 와야 한다")
        elif key == "소스":
            for kind, entries in value.items():
                if kind in spec[key] and isinstance(entries, M) and isinstance(spec[key][kind], M):
                    merge_named(spec[key][kind], entries, f"소스 > {kind}", rep)
                elif kind not in spec[key]:
                    spec[key][kind] = entries
                    spec[key].keypos[kind] = value.keypos[kind]
        else:
            merge_named(spec[key], value, key, rep)


# ---------------------------------------------------------------- 검사


def texts(value):
    if value is None:
        return []
    if isinstance(value, L):
        return [item for item in value if isinstance(item, S) and item]
    if isinstance(value, S):
        return [value] if value else []
    return []


class Scope:
    def __init__(self, parent=None, params=()):
        self.parent = parent
        self.states = {}
        self.actions = set()
        self.params = set(params)
        self.in_list = bool(parent and parent.in_list)

    def chain(self):
        scope = self
        while scope:
            yield scope
            scope = scope.parent

    def state_kind(self, name):
        for scope in self.chain():
            if name in scope.states:
                return scope.states[name]
        return None

    def has_param(self, name):
        return any(name in scope.params for scope in self.chain())

    def has_action(self, name):
        return any(name in scope.actions for scope in self.chain())

    def names(self):
        found = []
        for scope in self.chain():
            found += list(scope.states) + list(scope.params)
        return found

    def action_names(self):
        found = []
        for scope in self.chain():
            found += list(scope.actions)
        return found


class Checker:
    def __init__(self, spec, rep):
        self.spec = spec
        self.rep = rep
        self.count = dict.fromkeys(
            ["화면", "컴포넌트", "상태", "동작", "단계", "문장 단계", "백그라운드 작업", "알림"], 0
        )
        self.edges = []
        self.runs = []
        self.timed_actions = set()
        self.incoming = set()

    # -- 공통 도구

    def as_map(self, value, pos, path):
        if isinstance(value, M):
            return value
        if isinstance(value, S) and not value:
            return M()
        self.rep.error(pos, path, "아래에 `이름:` 으로 시작하는 줄이 와야 한다")
        return M()

    def keys(self, mapping, allowed, path):
        for key in mapping:
            if key not in allowed:
                self.rep.error(
                    mapping.keypos[key], path, f"`{key}` {josa(key, '은/는')} 여기서 쓰는 낱말이 아니다.{suggest(key, allowed)}"
                )

    def enum(self, mapping, key, allowed, path):
        value = mapping.get(key)
        if value is None or (isinstance(value, S) and not value):
            return None
        if not isinstance(value, S) or value not in allowed:
            shown = value if isinstance(value, S) else "(목록)"
            self.rep.error(
                mapping.keypos[key],
                path,
                f"`{key}` 의 값 `{shown}` {josa(shown, '은/는')} 쓸 수 없다. 쓸 수 있는 값: {', '.join(allowed)}",
            )
            return None
        return value

    def need(self, mapping, key, path, question):
        value = mapping.get(key)
        if value is None or (isinstance(value, (S, L, M)) and len(value) == 0):
            self.rep.blank(mapping.pos, path, question)
            return False
        return True

    def notes(self, node, path):
        if isinstance(node, M):
            for key, value in node.items():
                if key == "미정":
                    for item in texts(value):
                        self.rep.add("미정", item.pos, path, str(item))
                else:
                    self.notes(value, path + [key])
        elif isinstance(node, L):
            for item in node:
                self.notes(item, path)

    # -- 색인

    def index(self):
        spec = self.spec
        self.keys(spec, TOP, [])
        self.app = self.as_map(spec.get("앱", S("")), spec.pos, ["앱"])
        sources = self.as_map(spec.get("소스", S("")), spec.pos, ["소스"])
        self.keys(sources, SOURCE, ["소스"])
        self.servers = self.as_map(sources.get("네트워크", S("")), sources.pos, ["소스", "네트워크"])
        self.disks = self.as_map(sources.get("디스크", S("")), sources.pos, ["소스", "디스크"])
        self.screens = self.as_map(spec.get("화면", S("")), spec.pos, ["화면"])
        self.flows = self.as_map(spec.get("흐름", S("")), spec.pos, ["흐름"])
        self.jobs = self.as_map(spec.get("백그라운드 작업", S("")), spec.pos, ["백그라운드 작업"])
        self.notis = self.as_map(spec.get("알림", S("")), spec.pos, ["알림"])
        self.screen_params = {}
        for name, screen in self.screens.items():
            params = texts(screen.get("받는 값")) if isinstance(screen, M) else []
            self.screen_params[name] = [str(p) for p in params]
        self.noti_params = {}
        for name, noti in self.notis.items():
            params = texts(noti.get("받는 값")) if isinstance(noti, M) else []
            self.noti_params[name] = [str(p) for p in params]
        default = self.app.get("기본")
        default = default if isinstance(default, M) else M()
        cases = default.get("경우")
        self.default_cases = set(cases) if isinstance(cases, M) else set()
        self.default_failure = bool(default.get("요청 실패"))

    # -- 블록별

    def check_app(self):
        app, path = self.app, ["앱"]
        if "앱" not in self.spec:
            self.rep.blank(self.spec.pos, path, "`앱` 블록에 이름과 시작 화면을 적는다")
            return
        self.keys(app, APP + COMMON, path)
        self.need(app, "이름", path, "앱 이름을 `이름`에 적는다")
        if self.need(app, "시작 화면", path, "앱을 켜면 처음 보이는 화면을 `시작 화면`에 적는다"):
            self.screen_ref(app["시작 화면"], path, "시작 화면")
        for tab in texts(app.get("탭")):
            self.screen_ref(tab, path, "탭")
        default = app.get("기본")
        if default is not None:
            default = self.as_map(default, app.keypos["기본"], path + ["기본"])
            self.keys(default, APP_DEFAULT, path + ["기본"])
            cases = default.get("경우")
            if cases is not None:
                cases = self.as_map(cases, default.keypos["경우"], path + ["기본", "경우"])
                self.keys(cases, ["로딩", "오류"], path + ["기본", "경우"])
            if default.get("요청 실패") is not None:
                self.check_steps(default["요청 실패"], path + ["기본", "요청 실패"], self.app_scope, "앱")

    def screen_ref(self, value, path, what):
        if value in self.screens:
            self.incoming.add(str(value))
            return True
        self.rep.error(
            value.pos,
            path,
            f"`{what}` {josa(what, '이/가')} 가리키는 화면 `{value}` {josa(value, '이/가')} 없다.{suggest(value, self.screens)}",
        )
        return False

    def check_sources(self):
        for name, server in self.servers.items():
            path = ["소스", "네트워크", name]
            server = self.as_map(server, self.servers.keypos[name], path)
            self.keys(server, SERVER + COMMON, path)
            self.need(server, "주소", path, "서버 주소를 `주소`에 적는다")
        for name, disk in self.disks.items():
            path = ["소스", "디스크", name]
            disk = self.as_map(disk, self.disks.keypos[name], path)
            self.keys(disk, DISK + COMMON, path)
            if self.need(disk, "종류", path, f"저장소 종류를 `종류`에 적는다 ({', '.join(DISK_KINDS)})"):
                self.enum(disk, "종류", DISK_KINDS, path)

    def check_states(self, states, path, scope):
        if states is None:
            return
        states = self.as_map(states, scope_pos(states), path)
        for name, state in states.items():
            self.count["상태"] += 1
            scope.states[name] = self.check_state(state, path + [name], states.keypos[name])

    def check_state(self, state, path, pos):
        state = self.as_map(state, pos, path)
        kind = state.get("소스")
        known = isinstance(kind, S) and kind in STATE_BY_KIND
        if known:
            required, optional = STATE_BY_KIND[kind]
        else:
            required, optional = [], [key for req, opt in STATE_BY_KIND.values() for key in req + opt]
        self.keys(state, STATE_COMMON + COMMON + required + optional, path)
        self.need(state, "값", path, STATE_QUESTION["값"])
        if not self.need(state, "소스", path, STATE_QUESTION["소스"]):
            return None
        if not known:
            self.enum(state, "소스", list(STATE_BY_KIND), path)
            return None
        for key in required:
            self.need(state, key, path, STATE_QUESTION[key])
        if kind == "네트워크":
            self.server_ref(state, path)
            keep = state.get("보관")
            allowed = ["없음", "메모리"] + list(self.disks)
            if isinstance(keep, S) and keep and keep not in allowed:
                self.rep.error(
                    keep.pos,
                    path,
                    f"`보관` 의 값 `{keep}` {josa(keep, '은/는')} 쓸 수 없다. 쓸 수 있는 값: {', '.join(allowed)}",
                )
        elif kind == "디스크":
            store = state.get("저장소")
            if isinstance(store, S) and store and store not in self.disks:
                self.rep.error(
                    store.pos,
                    path,
                    f"디스크 저장소 `{store}` {josa(store, '이/가')} `소스 > 디스크` 에 없다.{suggest(store, self.disks)}",
                )
        elif kind == "메모리":
            rotate = self.enum(state, "구성 변경에도 유지", YES_NO, path)
            killed = self.enum(state, "프로세스 종료에도 유지", YES_NO, path)
            if killed == "예" and rotate == "아니오":
                self.rep.error(
                    state.keypos["프로세스 종료에도 유지"],
                    path,
                    "프로세스 종료 뒤에도 남는 값은 구성 변경 뒤에도 남는다. `구성 변경에도 유지` 를 예로 적는다",
                )
        return str(kind)

    def server_ref(self, mapping, path):
        server = mapping.get("서버")
        if isinstance(server, S) and server:
            if server not in self.servers:
                self.rep.error(
                    server.pos,
                    path,
                    f"서버 `{server}` {josa(server, '이/가')} `소스 > 네트워크` 에 없다.{suggest(server, self.servers)}",
                )
        elif not self.servers:
            self.rep.blank(mapping.pos, path, "`소스 > 네트워크` 에 서버가 없다. 서버를 먼저 적는다")
        elif len(self.servers) > 1:
            self.rep.blank(mapping.pos, path, "서버가 둘 이상이다. 어느 서버인지 `서버`에 적는다")

    def check_actions(self, actions, path, scope, origin, need_when=True):
        if actions is None:
            return
        actions = self.as_map(actions, scope_pos(actions), path)
        for name, action in actions.items():
            self.count["동작"] += 1
            here = path + [name]
            action = self.as_map(action, actions.keypos[name], here)
            self.keys(action, ACTION + COMMON, here)
            if need_when:
                self.need(action, "언제", here, "무엇이 이 동작을 시작시키는지 `언제`에 적는다")
            elif action.get("언제"):
                self.timed_actions.add(name)
            self.enum(action, "겹치면", JOB_OVERLAP, here)
            if self.need(action, "한다", here, "무슨 일을 하는지 `한다`에 단계로 적는다"):
                self.check_steps(action["한다"], here, scope, origin if need_when else "@" + name, name)

    def check_steps(self, steps, path, scope, origin, label=""):
        if not isinstance(steps, L):
            self.rep.error(scope_pos(steps), path, "단계는 줄마다 `- ` 로 시작하는 목록으로 적는다")
            return
        for step in steps:
            self.count["단계"] += 1
            if isinstance(step, S):
                self.count["문장 단계"] += 1
                continue
            if not isinstance(step, M):
                self.rep.error(scope_pos(step), path, "단계는 `낱말: 대상` 한 줄이거나 문장 하나다")
                continue
            verbs = [key for key in step if key in VERBS]
            if len(verbs) != 1:
                unknown = [key for key in step if key not in VERBS and key != "조건"]
                hint = suggest(unknown[0], VERBS) if unknown and not verbs else ""
                self.rep.error(
                    step.pos, path, f"단계 하나에는 낱말 하나만 쓴다 ({', '.join(VERBS)}). 없는 일은 문장으로 적는다.{hint}"
                )
                continue
            verb = verbs[0]
            self.keys(step, [verb, "조건"] + STEP_OPTS[verb], path)
            target = step[verb]
            if isinstance(target, S) and not target:
                self.rep.blank(step.pos, path, f"`{verb}` 뒤에 대상을 적는다")
                continue
            if not isinstance(target, S):
                self.rep.error(step.pos, path, f"`{verb}` 뒤에 대상을 한 줄로 적는다")
                continue
            getattr(self, "step_" + VERBS_EN[verb])(step, target, path, scope, origin, label)
            for branch in ("성공하면", "실패하면"):
                if step.get(branch) is not None:
                    self.check_steps(step[branch], path + [branch], scope, origin, label)

    def step_move(self, step, target, path, scope, origin, label):
        self.enum(step, "방식", NAV_MODES, path)
        if target == "뒤로":
            return
        if target not in self.screens:
            self.rep.error(
                target.pos,
                path,
                f"`이동` 이 가리키는 화면 `{target}` {josa(target, '이/가')} 없다.{suggest(target, self.screens)}",
            )
            return
        self.incoming.add(str(target))
        self.edges.append((origin, str(target), label))
        self.passed(step, self.screen_params[target], path, "화면", target)

    def passed(self, step, wanted, path, kind, target):
        given = step.get("넘기는 값")
        given = given if isinstance(given, M) else M()
        for name in wanted:
            if name not in given:
                self.rep.error(
                    step.pos,
                    path,
                    f"{kind} `{target}` {josa(target, '이/가')} 받는 값 `{name}` {josa(name, '을/를')} `넘기는 값`에 적지 않았다",
                )
        for name in given:
            if name not in wanted:
                self.rep.error(
                    given.keypos[name],
                    path,
                    f"{kind} `{target}` {josa(target, '은/는')} `{name}` {josa(name, '을/를')} 받지 않는다.{suggest(name, wanted)}",
                )

    def step_request(self, step, target, path, scope, origin, label):
        self.server_ref(step, path)
        if origin.startswith("백그라운드 작업"):
            return
        if step.get("실패하면") is None and not self.default_failure:
            self.rep.blank(step.pos, path, "요청이 실패하면 어떻게 하는지 `실패하면`에 적거나 `앱 > 기본 > 요청 실패`에 적는다")

    def step_change(self, step, target, path, scope, origin, label):
        root = target.split(".")[0].strip()
        kind = scope.state_kind(root)
        if root == "항목":
            if not scope.in_list:
                self.rep.error(target.pos, path, "`항목` 은 종류가 목록인 컴포넌트 안에서만 쓴다")
        elif kind is None and root not in scope.names():
            self.rep.error(
                target.pos,
                path,
                f"`변경` 이 가리키는 상태 `{root}` {josa(root, '이/가')} 없다.{suggest(root, scope.names())}",
            )
        elif kind in ("계산", "기기"):
            self.rep.error(
                target.pos, path, f"`{root}` {josa(root, '은/는')} 소스가 {kind}{josa(kind, '이라서/라서')} 직접 바꿀 수 없다"
            )
        self.need(step, "값", path, f"`{target}` {josa(target, '을/를')} 무슨 값으로 바꾸는지 `값`에 적는다")

    def step_refresh(self, step, target, path, scope, origin, label):
        kind = scope.state_kind(target)
        if kind is None:
            self.rep.error(
                target.pos,
                path,
                f"`새로고침` 이 가리키는 상태 `{target}` {josa(target, '이/가')} 없다.{suggest(target, scope.names())}",
            )
        elif kind != "네트워크":
            self.rep.error(
                target.pos,
                path,
                f"`새로고침` 은 소스가 네트워크인 상태에만 쓴다. `{target}` {josa(target, '은/는')} {kind}{josa(kind, '이다/다')}",
            )

    def step_text(self, step, target, path, scope, origin, label):
        return

    def step_notify(self, step, target, path, scope, origin, label):
        if target not in self.notis:
            self.rep.error(
                target.pos, path, f"알림 `{target}` {josa(target, '이/가')} `알림` 에 없다.{suggest(target, self.notis)}"
            )
            return
        noti = self.notis[target]
        if isinstance(noti, M) and noti.get("보내는 곳") == "서버":
            self.rep.error(target.pos, path, f"`{target}` {josa(target, '은/는')} 서버가 보내는 알림이라 앱이 띄울 수 없다")
        self.passed(step, self.noti_params[target], path, "알림", target)

    def step_schedule(self, step, target, path, scope, origin, label):
        if target not in self.jobs:
            self.rep.error(
                target.pos, path, f"백그라운드 작업 `{target}` {josa(target, '이/가')} 없다.{suggest(target, self.jobs)}"
            )

    def step_run(self, step, target, path, scope, origin, label):
        self.runs.append((origin, str(target)))
        if not scope.has_action(target):
            self.rep.error(
                target.pos,
                path,
                f"`실행` 이 가리키는 동작 `{target}` {josa(target, '이/가')} 없다.{suggest(target, scope.action_names())}",
            )

    def check_body(self, body, path, scope, origin, in_list, kind=""):
        refs = texts(body.get("표시"))
        bound = set()
        for ref in refs:
            root = ref.split(".")[0].strip()
            if root == "항목":
                if not in_list:
                    self.rep.error(ref.pos, path, "`항목` 은 종류가 목록인 컴포넌트 안에서만 쓴다")
                continue
            state_kind = scope.state_kind(root)
            if state_kind:
                bound.add(state_kind)
            elif not scope.has_param(root):
                self.rep.error(
                    ref.pos,
                    path,
                    f"`표시` 가 가리키는 상태 `{root}` {josa(root, '이/가')} 없다. 고정 글자면 `문구` 에 적는다.{suggest(root, scope.names())}",
                )
        cases = body.get("경우")
        case_names = set()
        if cases is not None:
            cases = self.as_map(cases, body.keypos["경우"], path + ["경우"])
            case_names = set(cases)
            for name, content in cases.items():
                if isinstance(content, M):
                    here = path + ["경우", name]
                    self.keys(content, CASE_BODY + COMMON, here)
                    self.check_body(content, here, scope, origin, in_list)
                elif isinstance(content, S) and not content:
                    self.rep.blank(cases.keypos[name], path + ["경우"], f"`{name}` 일 때 무엇이 보이는지 적는다")
                elif not isinstance(content, S):
                    self.rep.error(cases.keypos[name], path + ["경우"], f"`{name}` 일 때 무엇이 보이는지 문장으로 적는다")
        if "네트워크" in bound:
            for case in ("로딩", "오류"):
                if case not in case_names and case not in self.default_cases:
                    self.rep.blank(
                        body.pos,
                        path,
                        f"서버에서 받는 값을 보여 준다. `경우` 에 `{case}` {josa(case, '을/를')} 적거나 `앱 > 기본 > 경우` 에 적는다",
                    )
        if kind == "목록" and bound and "비었음" not in case_names:
            self.rep.blank(body.pos, path, "목록이 비었을 때 무엇이 보이는지 `경우` 의 `비었음` 에 적는다")
        if kind == "입력칸":
            if len(refs) != 1:
                self.rep.blank(body.pos, path, "입력칸은 입력한 값이 들어갈 상태 하나를 `표시` 에 적는다")
            elif bound & {"계산", "기기"}:
                self.rep.error(
                    refs[0].pos, path, f"`{refs[0]}` {josa(refs[0], '은/는')} 소스가 계산이나 기기라서 입력으로 바꿀 수 없다"
                )
        self.check_actions(body.get("동작"), path + ["동작"], scope, origin)
        children = body.get("컴포넌트")
        if children is not None:
            children = self.as_map(children, body.keypos["컴포넌트"], path + ["컴포넌트"])
            for name, child in children.items():
                self.check_component(name, child, path + ["컴포넌트", name], scope, origin, in_list, children.keypos[name])

    def check_component(self, name, comp, path, scope, origin, in_list, pos):
        self.count["컴포넌트"] += 1
        comp = self.as_map(comp, pos, path)
        self.keys(comp, COMPONENT + COMMON, path)
        inner = Scope(scope)
        self.check_states(comp.get("상태"), path + ["상태"], inner)
        kind = comp.get("종류")
        kind = str(kind) if isinstance(kind, S) else ""
        inner.in_list = in_list or kind == "목록"
        self.check_body(comp, path, inner, origin, in_list or kind == "목록", kind)

    def check_flows(self):
        self.flow_scope = {}
        for name, flow in self.flows.items():
            path = ["흐름", name]
            flow = self.as_map(flow, self.flows.keypos[name], path)
            self.keys(flow, FLOW + COMMON, path)
            scope = Scope(self.app_scope)
            self.check_states(flow.get("상태"), path + ["상태"], scope)
            if isinstance(flow.get("동작"), M):
                scope.actions |= set(flow["동작"])
            self.check_actions(flow.get("동작"), path + ["동작"], scope, f"흐름 {name}", need_when=False)
            if self.need(flow, "화면", path, "이 흐름에 속한 화면 이름을 `화면`에 적는다"):
                for screen in texts(flow["화면"]):
                    if screen not in self.screens:
                        self.rep.error(
                            screen.pos, path, f"화면 `{screen}` {josa(screen, '이/가')} 없다.{suggest(screen, self.screens)}"
                        )
                    elif screen in self.flow_scope:
                        self.rep.error(screen.pos, path, f"화면 `{screen}` {josa(screen, '은/는')} 이미 다른 흐름에 들어 있다")
                    else:
                        self.flow_scope[str(screen)] = scope

    def check_screens(self):
        for name, screen in self.screens.items():
            self.count["화면"] += 1
            path = ["화면", name]
            screen = self.as_map(screen, self.screens.keypos[name], path)
            self.keys(screen, SCREEN + COMMON, path)
            self.enum(screen, "형태", SCREEN_FORMS, path)
            scope = Scope(self.flow_scope.get(name, self.app_scope), self.screen_params[name])
            self.check_states(screen.get("상태"), path + ["상태"], scope)
            if isinstance(screen.get("동작"), M):
                scope.actions |= set(screen["동작"])
            self.check_actions(screen.get("동작"), path + ["동작"], scope, name)
            children = screen.get("컴포넌트")
            if children is not None:
                children = self.as_map(children, screen.keypos["컴포넌트"], path + ["컴포넌트"])
                for child_name, child in children.items():
                    self.check_component(
                        child_name, child, path + ["컴포넌트", child_name], scope, name, False, children.keypos[child_name]
                    )
            if not screen.get("컴포넌트") and not screen.get("동작"):
                self.rep.blank(self.screens.keypos[name], path, "화면에 보이는 것을 `컴포넌트`에, 일어나는 일을 `동작`에 적는다")
            if screen.get("링크"):
                self.incoming.add(name)
            if screen.get("형태") == "위젯":
                self.incoming.add(name)

    def check_jobs(self):
        for name, job in self.jobs.items():
            self.count["백그라운드 작업"] += 1
            path = ["백그라운드 작업", name]
            job = self.as_map(job, self.jobs.keypos[name], path)
            self.keys(job, JOB + COMMON, path)
            self.need(job, "언제", path, "무엇이 이 작업을 시작시키는지 `언제`에 적는다")
            if self.need(job, "미뤄도 됨", path, "시스템이 실행을 늦춰도 되는지 `미뤄도 됨`에 예, 아니오로 적는다"):
                self.enum(job, "미뤄도 됨", YES_NO, path)
            self.need(job, "다시 시도", path, "실패하면 다시 시도하는지 `다시 시도`에 적는다. 안 하면 안 함이라고 적는다")
            if self.need(job, "겹치면", path, f"같은 작업이 이미 돌고 있으면 어떻게 하는지 `겹치면`에 적는다 ({', '.join(JOB_OVERLAP)})"):
                self.enum(job, "겹치면", JOB_OVERLAP, path)
            progress = job.get("진행 알림")
            if isinstance(progress, S) and progress and progress not in self.notis:
                self.rep.error(
                    progress.pos, path, f"알림 `{progress}` {josa(progress, '이/가')} `알림` 에 없다.{suggest(progress, self.notis)}"
                )
            scope = Scope(self.app_scope, [str(p) for p in texts(job.get("받는 값"))])
            if self.need(job, "한다", path, "무슨 일을 하는지 `한다`에 단계로 적는다"):
                self.check_steps(job["한다"], path, scope, f"백그라운드 작업: {name}", name)

    def check_notis(self):
        for name, noti in self.notis.items():
            self.count["알림"] += 1
            path = ["알림", name]
            noti = self.as_map(noti, self.notis.keypos[name], path)
            self.keys(noti, NOTI + COMMON, path)
            if self.need(noti, "보내는 곳", path, "서버가 보내는 푸시인지 앱이 직접 띄우는지 `보내는 곳`에 적는다 (서버, 앱)"):
                self.enum(noti, "보내는 곳", NOTI_FROM, path)
            self.enum(noti, "중요도", NOTI_LEVEL, path)
            if not noti.get("제목") and not noti.get("본문"):
                self.rep.blank(noti.pos, path, "알림에 보이는 글을 `제목`과 `본문`에 적는다")
            self.need(noti, "앱을 보고 있을 때", path, "앱을 보고 있는 중에 오면 어떻게 하는지 `앱을 보고 있을 때`에 적는다")
            scope = Scope(self.app_scope, self.noti_params[name])
            if self.need(noti, "동작", path, "알림을 누르면 무슨 일이 일어나는지 `동작`에 적는다"):
                self.check_actions(noti["동작"], path + ["동작"], scope, f"알림: {name}")

    def check_reachable(self):
        for name in self.screens:
            if name not in self.incoming:
                self.rep.blank(
                    self.screens.keypos[name], ["화면", name], "이 화면으로 들어오는 길이 없다. 다른 곳의 `이동` 이나 `링크` 가 필요하다"
                )

    def run(self):
        self.index()
        self.app_scope = Scope()
        self.check_sources()
        self.check_states(self.spec.get("상태"), ["상태"], self.app_scope)
        if isinstance(self.spec.get("동작"), M):
            self.app_scope.actions |= set(self.spec["동작"])
        self.check_app()
        self.check_actions(self.spec.get("동작"), ["동작"], self.app_scope, "앱", need_when=False)
        self.check_flows()
        self.check_screens()
        self.check_jobs()
        self.check_notis()
        self.resolve_runs()
        self.check_reachable()
        self.notes(self.spec, [])

    def resolve_runs(self):
        """이름 붙인 동작 안의 이동을, 그 동작을 실행한 곳에서 나가는 이동으로 바꾼다."""
        named = {}
        for origin, target, label in self.edges:
            if origin.startswith("@"):
                named.setdefault(origin[1:], []).append(target)
        calls = {}
        for origin, action in self.runs:
            calls.setdefault(origin, []).append(action)

        def targets(action, seen):
            if action in seen:
                return []
            seen = seen | {action}
            found = list(named.get(action, []))
            for inner in calls.get("@" + action, []):
                found += targets(inner, seen)
            return found

        resolved = [edge for edge in self.edges if not edge[0].startswith("@")]
        for origin, action in self.runs:
            if origin.startswith("@"):
                continue
            for target in targets(action, frozenset()):
                resolved.append((origin, target, action))
        for action in self.timed_actions:
            for target in targets(action, frozenset()):
                resolved.append(("앱", target, action))
        self.edges = resolved


VERBS_EN = {
    "이동": "move",
    "요청": "request",
    "변경": "change",
    "새로고침": "refresh",
    "안내": "text",
    "알림": "notify",
    "예약": "schedule",
    "취소": "schedule",
    "분석": "text",
    "기기": "text",
    "실행": "run",
}


def scope_pos(node):
    return getattr(node, "pos", None)


def mermaid(checker):
    lines = ["flowchart LR"]
    ids = {}

    def node_id(label):
        if label not in ids:
            ids[label] = f"n{len(ids) + 1}"
            shape = f'["{label}"]' if label in checker.screens else f'(["{label}"])'
            lines.append(f"  {ids[label]}{shape}")
        return ids[label]

    start = checker.app.get("시작 화면")
    if isinstance(start, S) and start in checker.screens:
        lines.append(f"  start((시작)) --> {node_id(str(start))}")
    seen = set()
    for origin, target, label in checker.edges:
        if (origin, target, label) in seen:
            continue
        seen.add((origin, target, label))
        arrow = f"-->|{label}|" if label else "-->"
        lines.append(f"  {node_id(origin)} {arrow} {node_id(target)}")
    return "\n".join(lines)


def dot_graph(checker):
    """화면 이동을 Graphviz DOT 으로 만든다. `dot -Tpng` 로 이미지를 뽑는다."""
    font = "Apple SD Gothic Neo"
    start = checker.app.get("시작 화면")
    start = str(start) if isinstance(start, S) else ""
    tabs = {str(tab) for tab in texts(checker.app.get("탭"))}
    lines = [
        "digraph screens {",
        "  rankdir=LR;",
        "  nodesep=0.35; ranksep=0.9;",
        f'  graph [fontname="{font}", bgcolor="white", pad=0.3];',
        f'  node [fontname="{font}", fontsize=13, shape=box, style="rounded,filled", fillcolor="white", color="#444444", margin="0.18,0.10"];',
        f'  edge [fontname="{font}", fontsize=10, color="#666666", fontcolor="#333333", arrowsize=0.7];',
    ]
    ids = {}

    def node_id(label):
        if label in ids:
            return ids[label]
        ids[label] = f"n{len(ids) + 1}"
        attrs = []
        if label in checker.screens:
            screen = checker.screens[label]
            form = screen.get("형태") if isinstance(screen, M) else None
            form = str(form) if isinstance(form, S) and form else "전체 화면"
            text = label if form == "전체 화면" else f"{label}\\n({form})"
            if label == start:
                attrs.append('fillcolor="#cfe3ff", penwidth=2')
            elif label in tabs:
                attrs.append('fillcolor="#e9f1ff"')
            if form != "전체 화면":
                attrs.append('style="rounded,filled,dashed"')
        else:
            text = label
            attrs.append('shape=ellipse, fillcolor="#eeeeee", color="#999999", fontsize=11')
        extra = (", " + ", ".join(attrs)) if attrs else ""
        lines.append(f'  {ids[label]} [label="{text}"{extra}];')
        return ids[label]

    for name in checker.screens:
        node_id(name)
    shown_tabs = [ids[tab] for tab in tabs if tab in ids]
    if shown_tabs:
        lines.append("  subgraph cluster_tabs {")
        lines.append(f'    label="탭"; fontname="{font}"; fontsize=11; fontcolor="#5577aa"; style="rounded,dashed"; color="#99aacc";')
        lines.append("    " + "; ".join(shown_tabs) + ";")
        lines.append("  }")
    merged = {}
    for origin, target, label in checker.edges:
        labels = merged.setdefault((origin, target), [])
        if label and label not in labels:
            labels.append(label)
    for (origin, target), labels in merged.items():
        text = "\\n".join(labels)
        lines.append(f'  {node_id(origin)} -> {node_id(target)} [label="{text}"];')
    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="앱 기획 표준 v0.1 검사기")
    parser.add_argument("paths", nargs="+", help="명세 파일이나 폴더")
    parser.add_argument("--strict", action="store_true", help="빈칸과 미정도 실패로 본다")
    parser.add_argument("--graph", action="store_true", help="화면 이동을 Mermaid 로 찍는다")
    parser.add_argument("--dot", action="store_true", help="화면 이동을 Graphviz DOT 으로 찍는다 (dot -Tpng 로 이미지를 만든다)")
    args = parser.parse_args()

    rep = Report()
    spec = M()
    spec.pos = None
    files = collect_files(args.paths)
    for file in files:
        for text, offset in read_blocks(file):
            part = load_text(text, str(file), offset, rep)
            if part is not None:
                if spec.pos is None:
                    spec.pos = part.pos
                merge(spec, part, rep)
    if spec.pos is None:
        sys.exit("읽을 명세가 없다. .yaml 파일이나 ```yaml 블록이 든 .md 파일을 준다")

    checker = Checker(spec, rep)
    checker.run()

    if args.graph:
        print(mermaid(checker))
        return 0
    if args.dot:
        print(dot_graph(checker))
        return 0

    multi = len(files) > 1
    for level in ("오류", "빈칸", "미정"):
        found = rep.items[level]
        if not found:
            continue
        print(f"{level} {len(found)}건")
        for pos, path, msg in found:
            where = ""
            if pos:
                where = f"{Path(pos[0]).name}:{pos[1]}" if multi else f"{pos[1]}행"
            head = " ".join(part for part in (where, path) if part)
            print(f"  {head}: {msg}" if head else f"  {msg}")
        print()
    count = checker.count
    checked = count["단계"] - count["문장 단계"]
    print(
        "요약: "
        + ", ".join(f"{key} {count[key]}" for key in ("화면", "컴포넌트", "상태", "동작", "백그라운드 작업", "알림"))
        + f", 단계 {count['단계']} (낱말 {checked}, 문장 {count['문장 단계']})"
    )
    failed = bool(rep.items["오류"]) or (args.strict and (rep.items["빈칸"] or rep.items["미정"]))
    print("결과: 실패" if failed else "결과: 통과")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
