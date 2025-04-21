from dataclasses import dataclass
from typing import List
from .exam import Exam
from .period import Period
from .room import Room

@dataclass(frozen=True)
class Booking:
    exam: Exam
    period: Period
    rooms: List[Room]

    def __str__(self) -> str:
        rooms_str = ", ".join(str(room) for room in self.rooms)
        return f"[[ {self.exam} | {self.period} | {rooms_str} ]]"