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

    def distance_to_feasibility(self) -> int:   # Computation of number of hard constraint violations
        return (
            self.conflicting_exams() +                  # Conflicting exams scheduled in the same period    (14)
            self.overbooked_periods() +                 # Room over-occupancy                               (12)
            self.too_short_periods() +                  # Period over-utilization                           (13)
            self.period_constraint_violations() +       # Period-related constraint  violations             (15, 16, 17)
            self.room_constraint_violations()           # Room-related constraint violations                (18)
        )

    def soft_constraint_violations(self) -> int:    # Computation of number of soft constraint violations
        return (
            self.two_in_a_row_penalty() +       # Two exams in a row        (19)
            self.two_in_a_day_penalty() +       # Two exams in a day        (20)
            self.period_spread_penalty() +      # Period spread issues      (21)
            self.mixed_durations_penalty() +    # Mixed durations           (23)
            self.frontload_penalty() +          # Large exam constraints    (26)
            self.period_penalty() +             # Period penalties          (27)
            self.room_penalty()                 # Room penalties            (28)
        )

    # TODO: Placeholder methods 
    def conflicting_exams(self) -> int:                 # Returns the number of conflicting exams scheduled in the same period
        return 0

    def overbooked_periods(self) -> int:                # Returns the number of periods where seating capacity is exceeded
        return 0 

    def too_short_periods(self) -> int:                 # Returns the number of periods where the exam duration exceeds available time
        return 0

    def period_constraint_violations(self) -> int:      # Returns the number of period-related constraint violations
        return 0

    def room_constraint_violations(self) -> int:        # Returns the number of room-related constraint violations
        return 0

    def two_in_a_row_penalty(self) -> int:              # Returns the penalty for scheduling two exams consecutively
        return 0

    def two_in_a_day_penalty(self) -> int:              # Returns the penalty for scheduling two exams on the same day
        return 0

    def frontload_penalty(self) -> int:                 # Returns the penalty for frontloading large exams
        """."""
        return 0

    def mixed_durations_penalty(self) -> int:           # Returns the penalty for mixed exam durations in the same period
        return 0

    def period_spread_penalty(self) -> int:             # Returns the penalty for scheduling exams too closely together
        return 0

    def room_penalty(self) -> int:                      # Returns the penalty for room-related soft constraint violations
        return 0

    def period_penalty(self) -> int:                    # Returns the penalty for period-related soft constraint violations
        return 0
