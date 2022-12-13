"""
Implements logical expressions in the context of course requirements.
"""


from abc import abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated, Any, ClassVar, Literal, Union


class BaseExpr(BaseModel):
    """
    A logical expression.
    The requirements that a student must uphold in order to take a course is expressed
    through a combination of expressions.
    """

    hash: Annotated[int, Field(exclude=True)] = 0

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.hash = self.compute_hash()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def compute_hash(self) -> int:
        pass


class BaseOp(BaseExpr):
    """
    A logical connector between expressions.
    May be AND or OR.
    """

    neutral: ClassVar[bool]
    children: tuple["Expr", ...]

    @staticmethod
    @abstractmethod
    def op(a: bool, b: bool) -> bool:
        pass

    def __str__(self):
        op = "y" if self.neutral else "o"
        s = ""
        for child in self.children:
            if s != "":
                s += f" {op} "
            if isinstance(child, BaseOp):
                s += f"({child})"
            else:
                s += str(child)
        return s

    def compute_hash(self) -> int:
        h = hash(("op", self.neutral))
        for child in self.children:
            h = hash((h, child.hash))
        return h

    @staticmethod
    def create(neutral: bool, children: tuple["Expr", ...]) -> "Operator":
        """
        Build an AND node or an OR node in a generic way, using the neutral element to
        distinguish between them.
        In other words, if `neutral` is true, build an AND node, otherwise build an OR
        node.
        """
        if neutral:
            return And(children=children)
        else:
            return Or(children=children)


class And(BaseOp):
    """
    Logical AND connector.
    Only satisfied if all of its children are satisfied.
    """

    expr: Literal["and"] = "and"
    neutral: ClassVar[bool] = True

    @staticmethod
    def op(a: bool, b: bool) -> bool:
        return a and b


class Or(BaseOp):
    """
    Logical OR connector.
    Only satisfied if at least one of its children is satisfied.
    """

    expr: Literal["or"] = "or"
    neutral: ClassVar[bool] = False

    @staticmethod
    def op(a: bool, b: bool) -> bool:
        return a or b


class Const(BaseExpr):
    """
    A constant, fixed value of True or False.
    """

    expr: Literal["const"] = "const"
    value: bool

    def __str__(self):
        return str(self.value)

    def compute_hash(self) -> int:
        return hash(("const", self.value))


class Level(Enum):
    """
    An academic level.
    """

    # TODO: Confirm this order, is it correct?
    PREGRADO = 1
    POSTITULO = 2
    MAGISTER = 3
    DOCTORADO = 4


class MinCredits(BaseExpr):
    """
    A restriction that is only satisfied if the total amount of credits in the previous
    semesters is over a certain threshold.
    """

    expr: Literal["cred"] = "cred"

    min_credits: int

    def __str__(self):
        return f"(Creditos >= {self.min_credits})"

    def compute_hash(self) -> int:
        return hash(("cred", self.min_credits))


class ReqLevel(BaseExpr):
    """
    Express that this course requires a certain academic level.
    """

    expr: Literal["lvl"] = "lvl"

    min_level: Level

    def __str__(self):
        return f"(Nivel = {self.min_level})"

    def compute_hash(self):
        return hash(("lvl", self.min_level))


class ReqSchool(BaseExpr):
    """
    Express that this course requires the student to belong to a particular school.
    """

    expr: Literal["school"] = "school"

    school: str

    # Require equality or inequality?
    equal: bool

    def __str__(self):
        eq = "=" if self.equal else "!="
        return f"(Facultad {eq} {self.school})"

    def compute_hash(self) -> int:
        return hash(("school", self.school, self.equal))


class ReqProgram(BaseExpr):
    """
    Express that this course requires the student to belong to a particular program.
    """

    expr: Literal["program"] = "program"

    program: str

    # Require equality or inequality?
    equal: bool

    def __str__(self):
        eq = "=" if self.equal else "!="
        return f"(Programa {eq} {self.program})"

    def compute_hash(self) -> int:
        return hash(("program", self.program, self.equal))


class ReqCareer(BaseExpr):
    """
    Express that this course requires the student to belong to a particular career.
    """

    expr: Literal["career"] = "career"

    career: str

    # Require equality or inequality?
    equal: bool

    def __str__(self):
        eq = "=" if self.equal else "!="
        return f"(Carrera {eq} {self.career})"

    def compute_hash(self) -> int:
        return hash(("career", self.career, self.equal))


class ReqCourse(BaseExpr):
    """
    Require the student to have taken a course in the previous semesters.
    """

    expr: Literal["req"] = "req"

    code: str

    # Is this requirement a corequirement?
    coreq: bool

    def __str__(self):
        if self.coreq:
            return f"{self.code}(c)"
        else:
            return self.code

    def compute_hash(self) -> int:
        return hash(("req", self.code, self.coreq))


Atom = Union[Const, MinCredits, ReqLevel, ReqSchool, ReqProgram, ReqCareer, ReqCourse]

Operator = Union[And, Or]

Expr = Annotated[
    Union[
        Operator,
        Atom,
    ],
    Field(discriminator="expr"),
]

And.update_forward_refs()
Or.update_forward_refs()
Const.update_forward_refs()
MinCredits.update_forward_refs()
ReqLevel.update_forward_refs()
ReqSchool.update_forward_refs()
ReqProgram.update_forward_refs()
ReqCareer.update_forward_refs()
ReqCourse.update_forward_refs()
