from dataclasses import dataclass

@dataclass(frozen=True) # Makes the attributes immutable
class PeriodHardConstraint:
    exam_one: int           # Identifier of first exam for the constraint
    constraint_type: str    # Constraint type (one of EXAM_COINCIDENCE, EXCLUSION, and AFTER)
    exam_two: int           # Identifier of second exam for the constraint
