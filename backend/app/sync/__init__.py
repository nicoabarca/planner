"""
Update local database with an official but ugly source.
Currently using unofficial sources until we get better API access.
"""

import time
from collections import OrderedDict

from fastapi import HTTPException
from prisma.models import (
    CachedCurriculum as DbCachedCurriculum,
)
from prisma.models import (
    Course as DbCourse,
)
from prisma.models import (
    Equivalence as DbEquivalence,
)
from prisma.models import (
    EquivalenceCourse as DbEquivalenceCourse,
)
from prisma.models import (
    Major as DbMajor,
)
from prisma.models import (
    MajorMinor as DbMajorMinor,
)
from prisma.models import (
    Minor as DbMinor,
)
from prisma.models import (
    Title as DbTitle,
)

from app.plan.courseinfo import pack_course_details
from app.plan.validation.curriculum.tree import (
    Curriculum,
    CurriculumSpec,
)
from app.settings import settings
from app.sync import buscacursos_dl
from app.sync.curriculums.collate import collate_plans
from app.sync.curriculums.storage import CurriculumStorage
from app.sync.siding import translate as siding_translate
from app.user.auth import UserKey
from app.user.info import StudentContext

_CACHED_CURRICULUM_ID: str = "cached-course-info"


async def run_upstream_sync(
    *,
    courses: bool,
    curriculums: bool,
    offer: bool,
    packedcourses: bool,
):
    """
    Populate database with "official" data.

    NOTE: This function should only be called from a startup script, before any workers
    load.
    """

    if offer:
        print("syncing curriculum offer...")
        # Clear available programs
        await DbMajor.prisma().delete_many()
        await DbMinor.prisma().delete_many()
        await DbTitle.prisma().delete_many()
        await DbMajorMinor.prisma().delete_many()
        # Refetch available programs
        await siding_translate.load_siding_offer_to_database()

    if curriculums or courses:
        # If we delete courses, we must also delete equivalences (because equivalences
        # reference courses)
        # If we delete equivalences, we must also delete curriculums (because
        # curriculums reference equivalences)
        print("deleting stored equivalences...")
        await DbEquivalenceCourse.prisma().delete_many()
        await DbEquivalence.prisma().delete_many()

    if courses:
        print("syncing course database...")
        # Clear previous courses
        await DbCourse.prisma().delete_many()
        # Get course data from "official" source
        # Currently we have no official source
        await buscacursos_dl.fetch_to_database()

    if curriculums or packedcourses or courses:
        # If we updated the courses, we must update the packed courses too

        print("updating packed course details...")
        # Pack course details from main course database
        await pack_course_details()

    if curriculums or courses:
        # If we updated the courses, we must update the curriculums too, because the
        # equivalences reference the courses and to regenerate the equivalences we must
        # regenerate the curriculums

        # Equivalences and curriculums are sourced from various places
        print("deleting curriculum cache...")
        await DbCachedCurriculum.prisma().delete_many()
        print("syncing all curriculums...")
        storage = await collate_plans()
        await DbCachedCurriculum.prisma().create(
            {
                "id": _CACHED_CURRICULUM_ID,
                "curriculums": storage.json(),
            },
        )


_curriculum_cache: CurriculumStorage | None = None


async def get_curriculum(spec: CurriculumSpec) -> Curriculum:
    """
    Get the full curriculum definition for a particular curriculum spec.

    NOTE: Some users of this function, in particular `app.plan.generation`, modify the
    returned `Curriculum`.
    Therefore, each call to `get_curriculum` should result in a fresh curriculum.
    """

    global _curriculum_cache

    if _curriculum_cache is None:
        cached = await DbCachedCurriculum.prisma().find_unique(
            {
                "id": _CACHED_CURRICULUM_ID,
            },
        )
        if cached is None:
            raise Exception(
                "curriculum cache not found in db (maybe startup script was not run?)",
            )
        _curriculum_cache = CurriculumStorage.parse_raw(cached.curriculums)
    out = Curriculum.empty()

    # Fetch major (or common plan)
    curr = _curriculum_cache.get_major(spec)
    if curr is None:
        raise HTTPException(404, "major not found")
    out.extend(curr)

    # Fetch minor
    if spec.has_minor():
        curr = _curriculum_cache.get_minor(spec)
        if curr is None:
            raise HTTPException(404, "minor not found")
        out.extend(curr)

    # Fetch title
    if spec.has_title():
        curr = _curriculum_cache.get_title(spec)
        if curr is None:
            raise HTTPException(404, "title not found")
        out.extend(curr)

    return out


# TODO: Move this to redis
_student_context_cache: OrderedDict[str, tuple[StudentContext, float]] = OrderedDict()


async def get_student_data(user: UserKey) -> StudentContext:
    # Use entries in cache
    if user.rut in _student_context_cache:
        return _student_context_cache[user.rut][0]

    # Delete old entries from cache
    now = time.monotonic()
    while _student_context_cache:
        rut, (_ctx, expiration) = next(iter(_student_context_cache.items()))
        if now <= expiration:
            break
        _student_context_cache.pop(rut)

    # Request user context from SIDING
    print(f"fetching user data for student {user.rut} from SIDING...")
    try:
        info = await siding_translate.fetch_student_info(user.rut)
        passed, in_course = await siding_translate.fetch_student_previous_courses(
            user.rut,
            info,
        )
    except ValueError as err:
        # TODO: Refactor ValueError to use a custom exception
        if "Not a valid" in str(err):
            raise HTTPException(
                403,
                "User is not a valid engineering student.",
            ) from err
        raise ValueError from err

    ctx = StudentContext(
        info=info,
        passed_courses=passed,
        current_semester=len(passed) - (1 if in_course else 0),
        next_semester=len(passed),
    )

    # Add to cache and return
    _student_context_cache[user.rut] = (
        ctx,
        time.monotonic() + settings.student_info_expire,
    )
    return ctx
