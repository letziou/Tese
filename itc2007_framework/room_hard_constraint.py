from dataclasses import dataclass

@dataclass(frozen=True)
class RoomHardConstraint:
    exam_number: int           # Identifier of exam for the constraint
    constraint_type: str       # Constraint type (should always be ROOM_EXCLUSIVE) 
