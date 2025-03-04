from dataclasses import dataclass
from typing import List

@dataclass(frozen=True) # Makes the attributes immutable
class Exam:
    number: int             # identifier of the exam.
    duration: int           # duration of the exam.
    students: List[str]     # list of students partaking the exam

    def __str__(self) -> str:
        return f"Exam(id={self.number}, duration={self.duration}, #students={len(self.students)})"
