import traceback
from ..validate.models import (
    And,
    CourseCorequirement,
    Course,
    CourseRules,
    Expression,
    Level,
    MinCredits,
    Or,
    ReqCareer,
    ReqLevel,
    ReqNotCareer,
    ReqNotProgram,
    ReqNotSchool,
    ReqProgram,
    ReqSchool,
    CourseRequirement,
)
import requests
import pydantic
from pydantic import BaseModel
from typing import Callable, Dict, List


class BcSection(BaseModel):
    nrc: str
    teachers: str
    schedule: Dict[str, List[str]]
    format: str
    campus: str
    is_english: bool
    is_removable: bool
    is_special: bool
    total_quota: int


class BcCourse(BaseModel):
    name: str
    credits: int
    requirements: str
    connector: str
    restrictions: str
    program: str
    school: str
    area: str
    category: str
    sections: Dict[str, BcSection]


BcData = Dict[str, Dict[str, BcCourse]]


class BcParser:
    s: str
    i: int
    is_restr: bool

    def __init__(self, s: str, is_restr: bool):
        self.s = s
        self.i = 0
        self.is_restr = is_restr

    def take(self, cond: Callable[[str], bool]):
        prv = self.i
        while self.i < len(self.s) and cond(self.s[self.i]):
            self.i += 1
        return self.s[prv : self.i]

    def trim(self):
        return self.take(str.isspace)

    def eof(self):
        return self.i >= len(self.s)

    def bail(self, msg: str):
        ty = "restrictions" if self.is_restr else "requirements"
        raise Exception(f'invalid {ty} "{self.s}" around character {self.i}: {msg}')

    def ensure(self, cond: bool, msg: str):
        if not cond:
            self.bail(msg)

    def peek(self, n: int = 1):
        n = self.i + n
        if n > len(self.s):
            n = len(self.s)
        return self.s[self.i : n]

    def pop(self, n: int = 1):
        prv = self.i
        self.i += n
        if self.i > len(self.s):
            self.i = len(self.s)
        return self.s[prv : self.i]

    def parse_level(self, cmp: str, rhs: str) -> ReqLevel:
        self.ensure(cmp == "=", "expected = operator for level")
        if rhs == "Pregrado":
            lvl = Level.PREGRADO
        elif rhs == "Postitulo":
            lvl = Level.POSTITULO
        elif rhs == "Magister":
            lvl = Level.MAGISTER
        elif rhs == "Doctorado":
            lvl = Level.DOCTORADO
        else:
            self.bail("invalid academic level")
        return ReqLevel(min_level=lvl)

    def parse_property_eq(
        self, name: str, build: Callable[[bool, str], Expression], cmp: str, rhs: str
    ) -> Expression:
        if cmp == "=":
            return build(True, rhs)
        elif cmp == "<>":
            return build(False, rhs)
        else:
            self.bail(f"expected = or <> operator for {name}")

    def parse_credits(self, cmp: str, rhs: str) -> MinCredits:
        self.ensure(cmp == ">=", "expected >= operator for credits")
        try:
            cred = int(rhs)
        except ValueError:
            self.bail("invalid minimum credits")
        return MinCredits(min_credits=cred)

    def parse_restr(self) -> Expression:
        lhs = self.take(lambda c: c.isalnum() or c.isspace()).strip()
        self.trim()
        cmp = self.take(lambda c: c in "<=>")
        self.trim()
        rhs = self.take(lambda c: c != ")").strip()
        self.ensure(len(lhs) > 0, "expected an lhs")
        self.ensure(len(cmp) > 0, "expected a comparison operator")
        self.ensure(len(rhs) > 0, "expected an rhs")
        if lhs == "Nivel":
            return self.parse_level(cmp, rhs)
        elif lhs == "Escuela":
            return self.parse_property_eq(
                "school",
                lambda x, y: ReqSchool(school=y) if x else ReqNotSchool(school=y),
                cmp,
                rhs,
            )
        elif lhs == "Programa":
            return self.parse_property_eq(
                "program",
                lambda x, y: ReqProgram(program=y) if x else ReqNotProgram(program=y),
                cmp,
                rhs,
            )
        elif lhs == "Carrera":
            return self.parse_property_eq(
                "career",
                lambda x, y: ReqCareer(career=y) if x else ReqNotCareer(career=y),
                cmp,
                rhs,
            )
        elif lhs == "Creditos":
            return self.parse_credits(cmp, rhs)
        else:
            self.bail(f"unknown lhs '{lhs}'")

    def parse_req(self) -> Expression:
        code = self.take(str.isalnum)
        self.ensure(len(code) > 0, "expected a course code")
        self.trim()
        if self.peek() == "(":
            self.pop()
            self.ensure(self.pop(2) == "c)", "expected (c)")
            return CourseCorequirement(code=code)
        else:
            return CourseRequirement(code=code)

    def parse_unit(self) -> Expression:
        self.trim()
        self.ensure(not self.eof(), "expected an expression")

        # Parse parenthesized unit
        if self.peek() == "(":
            self.pop()
            inner = self.parse_orlist()
            self.trim()
            self.ensure(self.pop() == ")", "expected a closing parentheses")
            return inner

        # Parse unit
        if self.is_restr:
            return self.parse_restr()
        else:
            return self.parse_req()

    def parse_andlist(self) -> Expression:
        inner: List[Expression] = []
        while True:
            inner.append(self.parse_unit())
            self.trim()
            nxt = self.peek().lower()
            if nxt == "" or nxt == ")" or nxt == "o":
                break
            elif nxt == "y":
                self.pop()
            else:
                self.bail("expected the end of the expression or a connector")
        if len(inner) == 1:
            return inner[0]
        else:
            return And(children=inner)

    def parse_orlist(self) -> Expression:
        inner: List[Expression] = []
        while True:
            inner.append(self.parse_andlist())
            self.trim()
            nxt = self.peek().lower()
            if nxt == "" or nxt == ")":
                break
            elif nxt == "o":
                self.pop()
            else:
                self.bail("expected the end of the expression or a connector")
        if len(inner) == 1:
            return inner[0]
        else:
            return Or(children=inner)


def parse_reqs(reqs: str) -> Expression:
    return BcParser(reqs, is_restr=False).parse_orlist()


def parse_restr(restr: str) -> Expression:
    return BcParser(restr, is_restr=True).parse_orlist()


def parse_deps(c: BcCourse) -> Expression:
    deps = None
    if c.requirements != "No tiene":
        deps = parse_reqs(c.requirements)
    if c.restrictions != "No tiene":
        restr = parse_restr(c.restrictions)
        if deps is None:
            deps = restr
        else:
            if c.connector == "y":
                deps = And(children=[deps, restr])
            elif c.connector == "o":
                deps = Or(children=[deps, restr])
            else:
                raise Exception(f"invalid req/restr connector {c.connector}")
    if deps is None:
        deps = And(children=[])
    return deps


def fetch_and_translate() -> CourseRules:
    # Fetch json blob from an unofficial source
    dl_url = (
        "https://github.com/negamartin/buscacursos-dl/releases/download"
        + "/2022-2/courses-2022-2.json"
    )
    print(f"  downloading course data from {dl_url}...")
    # TODO: Use an async HTTP client
    resp = requests.request("GET", dl_url)
    resp.raise_for_status()
    if resp.encoding is None:
        resp.encoding = "UTF-8"
    # Parse JSON
    print("  parsing JSON...")
    data = pydantic.parse_raw_as(BcData, resp.text)
    # Extract latest semester
    _semester, data = max(data.items())
    # Convert to a cleaner format
    print("  processing courses...")
    courses = {}
    for code, c in data.items():
        try:
            req = parse_deps(c)
            course = Course(code=code, credits=c.credits, requires=req)
            courses[code] = course
        except Exception:
            print(f"failed to process course {code}:")
            print(traceback.format_exc())
    return CourseRules(courses=courses)
