from typing import Optional

from .user import validate_against_owner

from ...user.info import StudentContext
from .curriculum.diagnose import diagnose_curriculum
from .courses.validate import CourseInstance, ValidationContext, is_satisfied
from ..courseinfo import CourseInfo, course_info
from ...sync import get_curriculum
from .diagnostic import ValidationResult
from ..plan import ValidatablePlan


async def diagnose_plan(
    plan: ValidatablePlan, user_ctx: Optional[StudentContext]
) -> ValidationResult:
    """
    Validate a career plan, checking that all pending courses can actually be taken
    (ie. validate their dependencies), and also check that if the plan is followed the
    user will get their set major/minor/title degree.
    """
    courseinfo = await course_info()
    curriculum = await get_curriculum(plan.curriculum)
    out = ValidationResult.empty(plan)

    # Ensure course requirements are met
    course_ctx = ValidationContext(courseinfo, plan, user_ctx)
    course_ctx.validate_all(out)

    # Ensure the given curriculum is fulfilled
    diagnose_curriculum(courseinfo, curriculum, plan, user_ctx, out)

    # Validate against user context, if there is any context
    if user_ctx is not None:
        validate_against_owner(plan, user_ctx, out)

    return out


def quick_validate_dependencies(
    courseinfo: CourseInfo,
    plan: ValidatablePlan,
    sem: int,
    index: int,
) -> bool:
    """
    Validate only the dependencies of the course at the given position.
    """
    course = plan.classes[sem][index]
    info = courseinfo.try_course(course.code)
    if info is None:
        return False
    course_ctx = ValidationContext(courseinfo, plan, user_ctx=None)
    return is_satisfied(
        course_ctx,
        CourseInstance(code=course.code, sem=sem, index=index),
        info.deps,
    )
