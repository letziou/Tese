from dataclasses import dataclass

@dataclass(frozen=True) # Makes the attributes immutable
class PeriodHardConstraint:
    exam_one: int           # identifier of first exam for the constraint
    constraint_type: str    # constraint type (one of EXAM_COINCIDENCE, EXCLUSION, and AFTER)
    exam_two: int           # identifier of second exam for the constraint
