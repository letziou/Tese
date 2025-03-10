from dataclasses import dataclass
from .exam import Exam
from .period import Period
from .room import Room

@dataclass(frozen=True)
class Booking:
    exam: Exam
    period: Period
    room: Room

    def __str__(self) -> str:
        return f"[[ {self.exam} | {self.period} | {self.room} ]]"
