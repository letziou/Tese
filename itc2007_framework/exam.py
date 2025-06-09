from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Exam:
    number: int             # Identifier of the exam.
    duration: int           # Duration of the exam.
    students: List[str]     # List of students taking the exam
    exclusive: bool  = False     # Boolean that identifies if exam has exclusive constraint

    def set_exclusive(self):      # Permits to change the attribute full in frozen dataclass
        object.__setattr__(self, "exclusive", True)

    def __hash__(self):
        return hash(self.number)
    
    def __eq__(self, other):
        if not isinstance(other, Exam):
            return False
        return self.number == other.number

    def __str__(self) -> str:
        return f"Exam(id={self.number}, duration={self.duration}, #students={len(self.students)}, exclusive={self.exclusive})"
