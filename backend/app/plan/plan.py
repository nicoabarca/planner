from .validation.curriculum.tree import CurriculumSpec
from pydantic import BaseModel
from typing import Optional
from .course import PseudoCourse
from enum import Enum


class Level(int, Enum):
    """
    An academic level.
    """

    # TODO: Confirm this order, is it correct?
    PREGRADO = 1
    POSTITULO = 2
    MAGISTER = 3
    DOCTORADO = 4


class ValidatablePlan(BaseModel):
    """
    An academic plan submitted by a user.
    Contains all of the courses they have passed and intend to pass.
    Also contains all of the context associated with the user (e.g. their choice of
    major and minor).

    Including user context here allows plans to be validated without external context,
    allowing guests to simulate any plans they want to try out.
    """

    # NOTE: Modifying this class breaks all the JSON stored in the DB
    # Currently, we don't handle migrations at all.
    # Eventually, we will have to roll our own migration system if we allow
    # ValidatablePlans to be exportable/importable.

    # Classes per semester.
    classes: list[list[PseudoCourse]]
    # The first semester to validate.
    # Semesters before this semester are considered approved.
    next_semester: int
    # Academic level of the student
    level: Optional[Level]
    # Academic school (facultad) of the student
    school: Optional[str]
    # Academic program of the student (magisteres, doctorados, etc)
    program: Optional[str]
    # Career of the student
    career: Optional[str]
    # The curriculum that the user wants to pursue
    # Validate the plan against this curriculum
    curriculum: CurriculumSpec


class ClassId(BaseModel, frozen=True):
    """
    A somewhat stable identifier for a course instance within a plan.
    """

    # The code of the course of this class.
    code: str
    # The index of the instance of this course.
    instance: int
