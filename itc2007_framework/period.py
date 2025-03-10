from dataclasses import dataclass
from datetime import date, time, datetime

@dataclass(frozen=True) # Makes the attributes immutable
class Period:
    number: int     # Identifier of the period
    date: date      # Date of the period
    time: time      # Time of the period
    duration: int   # Duration of the period
    penalty: int    # Penalty of the period

    def get_datetime(self) -> datetime: # Returns a combined datetime object
        return datetime.combine(self.date, self.time)
    
    def __hash__(self):
        return hash(self.number)
    
    def __eq__(self, other):
        if not isinstance(other, Period):
            return False
        return self.number == other.number

    def __str__(self) -> str:
        return (f"Period(id={self.number}, date={self.date}, time={self.time}, duration={self.duration}, penalty={self.penalty})")
