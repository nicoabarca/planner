import traceback


from ..validation.courses.simplify import simplify
from ..validation.courses.logic import (
    Const,
    And,
    Or,
    Expr,
    Level,
    MinCredits,
    ReqCareer,
    ReqLevel,
    ReqProgram,
    ReqSchool,
)
from ..validation.courses.validate import ReqCourse
from prisma.models import Course as DbCourse
from prisma.types import CourseCreateWithoutRelationsInput
from prisma import Json
import requests
import pydantic
from pydantic import BaseModel
from typing import Callable


class BcSection(BaseModel):
    nrc: str
    teachers: str
    schedule: dict[str, list[str]]
    format: str
    campus: str
    is_english: bool
    is_removable: bool
    is_special: bool
    total_quota: int


class BcCourse(BaseModel):
    name: str
    credits: int
    req: str
    conn: str
    restr: str
    equiv: str
    program: str
    school: str
    area: str
    category: str
    sections: dict[str, BcSection]


BcData = dict[str, dict[str, BcCourse]]


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
        self, name: str, build: Callable[[bool, str], Expr], cmp: str, rhs: str
    ) -> Expr:
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

    def parse_restr(self) -> Expr:
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
                lambda eq, x: ReqSchool(school=x, equal=eq),
                cmp,
                rhs,
            )
        elif lhs == "Programa":
            return self.parse_property_eq(
                "program",
                lambda eq, x: ReqProgram(program=x, equal=eq),
                cmp,
                rhs,
            )
        elif lhs == "Carrera":
            return self.parse_property_eq(
                "career",
                lambda eq, x: ReqCareer(career=x, equal=eq),
                cmp,
                rhs,
            )
        elif lhs == "Creditos":
            return self.parse_credits(cmp, rhs)
        else:
            self.bail(f"unknown lhs '{lhs}'")

    def parse_req(self) -> Expr:
        code = self.take(str.isalnum)
        self.ensure(len(code) > 0, "expected a course code")
        self.trim()
        co = False
        if self.peek() == "(":
            self.pop()
            self.ensure(self.pop(2) == "c)", "expected (c)")
            co = True
        return ReqCourse(code=code, coreq=co)

    def parse_unit(self) -> Expr:
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

    def parse_andlist(self) -> Expr:
        inner: list[Expr] = []
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
            return And(children=tuple(inner))

    def parse_orlist(self) -> Expr:
        inner: list[Expr] = []
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
            return Or(children=tuple(inner))


def parse_reqs(reqs: str) -> Expr:
    return BcParser(reqs, is_restr=False).parse_orlist()


def parse_restr(restr: str) -> Expr:
    return BcParser(restr, is_restr=True).parse_orlist()


def parse_deps(c: BcCourse) -> Expr:
    deps = None
    if c.req != "No tiene":
        deps = parse_reqs(c.req)
    if c.restr != "No tiene":
        restr = parse_restr(c.restr)
        if deps is None:
            deps = restr
        else:
            if c.conn == "y":
                deps = And(children=(deps, restr))
            elif c.conn == "o":
                deps = Or(children=(deps, restr))
            else:
                raise Exception(f"invalid req/restr connector {c.conn}")
    if deps is None:
        deps = Const(value=True)
    return deps


async def fetch_to_database():
    # Fetch json blob from an unofficial source
    dl_url = (
        "https://github.com/negamartin/buscacursos-dl/releases/download"
        + "/2022-2-v2/courses-2022-2.json"
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
    # Process courses to place into database
    print("  processing courses...")
    db_input: list[CourseCreateWithoutRelationsInput] = []
    for code, c in data.items():
        try:
            deps = simplify(parse_deps(c))
            db_input.append(
                {
                    "code": code,
                    "name": c.name,
                    "credits": c.credits,
                    "deps": Json(deps.json()),
                    "program": c.program,
                    "school": c.school,
                    "area": None if c.area == "" else c.area,
                    "category": None if c.category == "" else c.category,
                }
            )
        except Exception:
            print(f"failed to process course {code}:")
            print(traceback.format_exc())
    # Remove previous course data from database
    print("  clearing previous courses...")
    await DbCourse.prisma().delete_many()
    # Put courses in database
    print("  storing courses in db...")
    await DbCourse.prisma().create_many(data=db_input)
