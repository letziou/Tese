from dataclasses import dataclass
from itc2007_framework.exam import Exam
from itc2007_framework.period import Period
from itc2007_framework.room import Room

@dataclass(frozen=True)
class Booking:
    exam: Exam
    period: Period
    room: Room

    def __str__(self) -> str:
        return f"[[ {self.exam} | {self.period} | {self.room} ]]"
