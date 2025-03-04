from dataclasses import dataclass
from datetime import date, time, datetime

@dataclass(frozen=True) # Makes the attributes immutable
class Period:
    number: int     # identifier of the period
    date: date      # date of the period
    time: time      # time of the period
    duration: int   # duration of the period
    penalty: int    # penalty of the period

    def get_datetime(self) -> datetime: # Returns a combined datetime object
        return datetime.combine(self.date, self.time)

    def __str__(self) -> str:
        return (f"Period(id={self.number}, date={self.date}, time={self.time}, duration={self.duration}, penalty={self.penalty})")
