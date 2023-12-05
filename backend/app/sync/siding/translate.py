"""
Transform the Siding format into something usable.
"""


import logging

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
from zeep.exceptions import Fault

from app.plan.course import ConcreteId, PseudoCourse
from app.plan.validation.curriculum.tree import (
    MajorCode,
    MinorCode,
    TitleCode,
    cyear_from_str,
)
from app.sync.siding import client
from app.sync.siding.client import (
    StringArray,
)
from app.user.info import StudentInfo
from app.user.key import Rut


def _decode_curriculum_versions(input: StringArray | None) -> list[str]:
    """
    SIDING returns lists of cyear codes (e.g. ["C2013", "C2020"]) as a convoluted
    `stringArray` type that is currently empty for some reason.
    Transform this type into a more manageable `list[str]`.
    """
    if input is None:
        # Curriculum lists are currently empty for some SIDING reason
        # We are currently patching through the mock
        # TODO: Once this is fixed remove patching code
        logging.warning("null curriculum version list")
        return []
    return input.strings.string


def _decode_period(period: str) -> tuple[int, int]:
    """
    Transform a string like "2020-2" to (2020, 2).
    """
    [year, sem] = period.split("-")
    return (int(year), int(sem))


def _semesters_elapsed(start: tuple[int, int], end: tuple[int, int]) -> int:
    """
    Calculate the difference between two periods as a signed number of semesters.
    """
    # Clamp to [1, 2] to handle TAV (semester 3, which should be treated as semester 2)
    s_sem = min(2, max(1, start[1]))
    e_sem = min(2, max(1, end[1]))
    return (end[0] - start[0]) * 2 + (e_sem - s_sem)


async def load_siding_offer_to_database():
    """
    Call into the SIDING webservice and fetch majors, minors and titles.
    """

    print("loading major/minor/title offer to database...")

    print("  loading majors")
    p_majors, p_minors, p_titles = (
        client.get_majors(),
        client.get_minors(),
        client.get_titles(),
    )
    majors = {major.CodMajor: major for major in await p_majors}
    for major in majors.values():
        for cyear in _decode_curriculum_versions(major.Curriculum):
            await DbMajor.prisma().create(
                data={
                    "cyear": cyear,
                    "code": major.CodMajor,
                    "name": major.Nombre,
                    "version": major.VersionMajor,
                },
            )

    print("  loading minors")
    minors = {minor.CodMinor: minor for minor in await p_minors}
    for minor in minors.values():
        for cyear in _decode_curriculum_versions(minor.Curriculum):
            await DbMinor.prisma().create(
                data={
                    "cyear": cyear,
                    "code": minor.CodMinor,
                    "name": minor.Nombre,
                    "version": minor.VersionMinor or "",
                    "minor_type": minor.TipoMinor,
                },
            )

    print("  loading titles")
    for title in await p_titles:
        for cyear in _decode_curriculum_versions(title.Curriculum):
            await DbTitle.prisma().create(
                data={
                    "cyear": cyear,
                    "code": title.CodTitulo,
                    "name": title.Nombre,
                    "version": title.VersionTitulo or "",
                    "title_type": title.TipoTitulo,
                },
            )

    print("  loading major-minor associations")
    p_major_minor = [
        (maj, client.get_minors_for_major(maj.CodMajor)) for maj in majors.values()
    ]
    for major, p_assoc_minors in p_major_minor:
        assoc_minors = await p_assoc_minors
        for cyear in _decode_curriculum_versions(major.Curriculum):
            for assoc_minor in assoc_minors:
                minor = minors[assoc_minor.CodMinor]
                if cyear not in _decode_curriculum_versions(minor.Curriculum):
                    continue
                await DbMajorMinor.prisma().create(
                    data={
                        "cyear": cyear,
                        "major": major.CodMajor,
                        "minor": minor.CodMinor,
                    },
                )


async def fetch_student_info(rut: Rut) -> StudentInfo:
    """
    MUST BE CALLED WITH AUTHORIZATION

    Request the basic student information for a given RUT from SIDING.
    """
    try:
        raw = await client.get_student_info(rut)
        career = "INGENIERÍA CIVIL"
        assert raw.Curriculo is not None and raw.Carrera == career

        return StudentInfo(
            full_name=raw.Nombre,
            cyear=raw.Curriculo,
            is_cyear_supported=cyear_from_str(raw.Curriculo) is not None,
            reported_major=MajorCode(raw.MajorInscrito) if raw.MajorInscrito else None,
            reported_minor=MinorCode(raw.MinorInscrito) if raw.MinorInscrito else None,
            reported_title=TitleCode(raw.TituloInscrito)
            if raw.TituloInscrito
            else None,
        )

    except (AssertionError, Fault) as err:
        if (isinstance(err, Fault) and "no pertenece" in err.message) or isinstance(
            err,
            AssertionError,
        ):
            raise ValueError("Not a valid engineering student") from err
        raise err


async def fetch_student_previous_courses(
    rut: Rut,
    info: StudentInfo,
) -> tuple[list[list[PseudoCourse]], bool]:
    """
    MUST BE CALLED WITH AUTHORIZATION

    Make a request to SIDING to find out the courses that the given student has passed.
    """

    raw = await client.get_student_done_courses(rut)
    semesters: list[list[PseudoCourse]] = []
    in_course: list[list[bool]] = []
    # Make sure semester 1 is always odd, adding an empty semester if necessary
    if raw:
        start_year = int(raw[0].Periodo.split("-")[0])
        start_period = (start_year, 1)
        for c in raw:
            sem = _semesters_elapsed(start_period, _decode_period(c.Periodo))
            while len(semesters) <= sem:
                semesters.append([])
            while len(in_course) <= sem:
                in_course.append([])
            if c.Estado.startswith("2"):
                # Failed course
                course = ConcreteId(code="#FAILED", failed=c.Sigla)
            else:
                # Approved course
                course = ConcreteId(code=c.Sigla)
            semesters[sem].append(course)
            currently_coursing = c.Estado.startswith("3")
            in_course[sem].append(currently_coursing)

    # Check if the last semester is currently being coursed
    last_semester_in_course = bool(in_course and in_course[-1] and all(in_course[-1]))

    return semesters, last_semester_in_course
