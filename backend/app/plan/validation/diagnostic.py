from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class FlatDiagnostic(BaseModel):
    course_code: Optional[str]
    is_warning: bool
    message: str


class FlatValidationResult(BaseModel):
    diagnostics: list[FlatDiagnostic]
    # Associates course codes with academic block names (superblocks).
    # Used to assign colors to each course depending on what purpose they serve.
    course_superblocks: dict[str, str]


class Diagnostic(BaseModel, ABC):
    """
    A diagnostic message, that may be associated to a course that the user is taking.
    """

    def course_code(self) -> Optional[str]:
        return None

    @abstractmethod
    def message(self) -> str:
        pass


class DiagnosticErr(Diagnostic):
    pass


class DiagnosticWarn(Diagnostic):
    pass


class ValidationResult(BaseModel):
    """
    Simply a list of diagnostics, in the same order that is shown to the user.
    """

    diagnostics: list[Diagnostic]
    # Associates course codes with academic block names (superblocks).
    # Used to assign colors to each course depending on what purpose they serve.
    course_superblocks: dict[str, str]

    def add(self, diag: Diagnostic):
        self.diagnostics.append(diag)

    def remove(self, indices: list[int]):
        for i, _diag in reversed(list(enumerate(self.diagnostics))):
            if i in indices:
                del self.diagnostics[i]

    def flatten(self) -> FlatValidationResult:
        flat_diags: list[FlatDiagnostic] = []
        for diag in self.diagnostics:
            flat = FlatDiagnostic(
                course_code=diag.course_code(),
                is_warning=isinstance(diag, DiagnosticWarn),
                message=diag.message(),
            )
            flat_diags.append(flat)
        return FlatValidationResult(
            diagnostics=flat_diags, course_superblocks=self.course_superblocks
        )
