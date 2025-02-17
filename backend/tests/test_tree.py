import pytest
from app.plan.validation.curriculum.tree import MajorCode, MinorCode, TitleCode
from pydantic import BaseModel, ValidationError


class CurriculumCodeTest(BaseModel):
    """
    Test the CurriculumCode class.
    """

    major_code: MajorCode = MajorCode("M123")
    minor_code: MinorCode = MinorCode("N123")
    title_code: TitleCode = TitleCode("40001")


def test_codes():
    """
    Test validation of major, minor and title codes.
    """

    with pytest.raises(ValidationError):
        CurriculumCodeTest(major_code=MajorCode("M1234"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(major_code=MajorCode("L123"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(major_code=MajorCode("DSJDF"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(major_code=MajorCode("N345"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(minor_code=MinorCode("M123"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(minor_code=MinorCode("N5332"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(minor_code=MinorCode("JSDJK"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(title_code=TitleCode("T123"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(title_code=TitleCode("1"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(title_code=TitleCode("FSDSFD"))

    with pytest.raises(ValidationError):
        CurriculumCodeTest(title_code=TitleCode("99999999"))

    # Test normal usage
    assert str(CurriculumCodeTest(major_code=MajorCode("M123")).major_code) == "M123"
    assert str(CurriculumCodeTest(minor_code=MinorCode("N123")).minor_code) == "N123"
    assert str(CurriculumCodeTest(title_code=TitleCode("40001")).title_code) == "40001"

    # Test deserialization from string
    d = {
        "major_code": "M123",
        "minor_code": "N123",
        "title_code": "40001",
    }
    parsed_curriculum = CurriculumCodeTest.parse_obj(d)
    assert parsed_curriculum.major_code == MajorCode("M123")
    assert parsed_curriculum.minor_code == MinorCode("N123")
    assert parsed_curriculum.title_code == TitleCode("40001")
    # Test serialization to string
    parsed_curriculum_dict = parsed_curriculum.dict()
    assert parsed_curriculum_dict["major_code"] == "M123"
    assert parsed_curriculum_dict["minor_code"] == "N123"
    assert parsed_curriculum_dict["title_code"] == "40001"
    # Check wrong deserialization
    with pytest.raises(ValidationError):
        CurriculumCodeTest.parse_obj({"major_code": "M1234"})
        CurriculumCodeTest.parse_obj({"minor_code": "N1234"})
        CurriculumCodeTest.parse_obj({"title_code": "400011"})
