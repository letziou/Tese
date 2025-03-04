from .exam_timetabling_problem import ExamTimetablingProblem
from .booking import Booking
from typing import List

class ExamTimetablingSolution:
    def __init__(self, problem: ExamTimetablingProblem, bookings: List[Booking]): 
        self.problem = problem      # The problem to solve
        self.bookings = bookings    # List of bookings for this solution

    def __str__(self) -> str:       # String representation of bookings. Each line represents the period and and room of each exam with them appearing as in the input file
        output = []
        for exam_num in range(len(self.bookings)):
            booking = next((b for b in self.bookings if b.exam.number == exam_num), None)
            if booking is None:
                raise RuntimeError("Unknown error: Booking not found for exam number.")
            
            output.append(f"{booking.period.number},{booking.room.number}")
        
        return "\n".join(output)