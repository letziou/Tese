from dataclasses import dataclass

@dataclass(frozen=True) # Makes the attributes immutable
class RoomHardConstraint:
    exam_number: int           # identifier of exam for the constraint
    constraint_type: str       # constraint type (should always be ROOM_EXCLUSIVE) 
