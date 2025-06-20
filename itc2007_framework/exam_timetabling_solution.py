from typing import List
from .exam_timetabling_problem import ExamTimetablingProblem
from .booking import Booking

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
    
    def distance_to_feasibility_period(self) -> int:   # Computation of number of hard constraint violations ignoring rooms
        return (
            self.conflicting_exams() +                  # Conflicting exams scheduled in the same period    (14)
            self.too_short_periods() +                  # Period over-utilization                           (13)
            self.period_constraint_violations()         # Period-related constraint  violations             (15, 16, 17)
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

    def conflicting_exams(self) -> int:                 # Returns the number of conflicting exams scheduled in the same period
        conflits = 0
        for booking_a in self.bookings:
            for booking_b in self.bookings:
                if booking_a.exam.number == booking_b.exam.number: 
                    continue

                period_clash = booking_a.period.number == booking_b.period.number       # Checking if both exams are in the same period
                students_share = self.problem.clash_matrix[booking_a.exam.number][booking_b.exam.number] > 0        # Checking if there are students that are enrolled in both exams
                if period_clash and students_share:     # If yes than conflits are increased
                    conflits += 1
        
        return conflits

    def overbooked_periods(self) -> int:                # Returns the number of periods where seating capacity is exceeded
        overbooked = 0
        for booking in self.bookings:
            if hasattr(booking.rooms, '__iter__') and not isinstance(booking.rooms, str):      # If booking.rooms is iterable (a list)
                total_capacity = sum(room.capacity for room in booking.rooms)
            else:
                total_capacity = booking.rooms.capacity
            if len(booking.exam.students) > total_capacity:
                overbooked += 1
        return overbooked

    def too_short_periods(self) -> int:                 # Returns the number of periods where the exam duration exceeds available time
        too_short = 0
        for booking in self.bookings:
            if booking.exam.duration > booking.period.duration:     # Checking if exam duration is bigger than period duration, if yes too_short is increased 
                too_short += 1

        return too_short

    def period_constraint_violations(self) -> int:      # Returns the number of period-related constraint violations
        period_violations = 0
        for constraint in self.problem.period_hard_constraints:
            # Finding the bookings associated with the exams in the constraint
            booking_one = next((b for b in self.bookings if b.exam.number == constraint.exam_one), None)
            booking_two = next((b for b in self.bookings if b.exam.number == constraint.exam_two), None)

            if booking_one is None or booking_two is None:      # Skips if one of the exams is not yet allocated
                continue

            if constraint.constraint_type == "EXAM_COINCIDENCE":
                if booking_one.period.number != booking_two.period.number:      # Checking if period is same for both exams, if not period_violations is increased
                    period_violations += 1
            
            elif constraint.constraint_type == "EXCLUSION":     # Checking if period is not the same for both exams, if yes period_violations is increased
                if booking_one.period.number == booking_two.period.number:
                    period_violations += 1
            
            elif constraint.constraint_type == "AFTER":
                if booking_one.period.get_datetime() < booking_two.period.get_datetime():       # Checking if exam one 
                    period_violations += 1

        return period_violations

    def room_constraint_violations(self) -> int:        # Returns the number of room-related constraint violations
        room_violations = 0
        for constraint in self.problem.room_hard_constraints:
            if constraint.constraint_type == "ROOM_EXCLUSIVE":
                booking = next((b for b in self.bookings if b.exam.number == constraint.exam_number), None)    # Finding the booking associated with the exam in the constraint
                if booking is None:     # Skips if exam has not yet been placed
                    continue
                
                # Check if booking.rooms is iterable
                if hasattr(booking.rooms, '__iter__') and not isinstance(booking.rooms, str):
                    rooms_to_check = booking.rooms
                else:
                    rooms_to_check = [booking.rooms]

                not_alone = False
                for room in rooms_to_check:
                    for b in self.bookings:
                        if b.exam.number != booking.exam.number and b.period.number == booking.period.number:
                            if hasattr(b.rooms, '__iter__') and not isinstance(b.rooms, str):
                                if any(room.number == other_room.number for other_room in b.rooms):
                                    not_alone = True
                                    break
                            else:
                                if room.number == b.rooms.number:
                                    not_alone = True
                                    break
                    if not_alone:
                        break
                if not_alone:
                    room_violations += 1
        
        return room_violations

    def two_in_a_row_penalty(self) -> int:              # Returns the penalty for scheduling two exams consecutively, for students
        row_penalty = 0
        weighting = next((w for w in self.problem.institutional_weightings if w.weightingType == "TWOINAROW"), None)       # Finding the weighting
        if weighting is None:       # If weight is not defined then penalty is 0
            return 0
        
        for i, booking_a in enumerate(self.bookings):
            for booking_b in self.bookings[i+1:]:

                in_a_row = abs(booking_a.period.number - booking_b.period.number) == 1      # Checking if periods are next to each other
                same_day = booking_a.period.date == booking_b.period.date       # Checking if date is the same

                if in_a_row and same_day:       # If exams are on neighboring periods and in the same day, then the penalty is added with the number of students in both exams multiplying by the weighting parameter
                    row_penalty += weighting.paramOne * self.problem.clash_matrix[booking_a.exam.number][booking_b.exam.number]

        return row_penalty

    def two_in_a_day_penalty(self) -> int:              # Returns the penalty for scheduling two exams on the same day
        day_penalty = 0
        weighting = next((w for w in self.problem.institutional_weightings if w.weightingType == "TWOINADAY"), None)       # Finding the weighting
        if weighting is None:       # If weight is not defined then penalty is 0
            return 0
        
        for i, booking_a in enumerate(self.bookings):
            for booking_b in self.bookings[i+1:]:

                not_in_a_row = abs(booking_a.period.number - booking_b.period.number) != 1      # Checking if periods are not next to each other
                same_day = booking_a.period.date == booking_b.period.date       # Checking if date is the same
                if not_in_a_row and same_day:       # If exams are on not neighboring periods but in the same day, then the penalty is added with the number of students in both exams multiplying by the weighting parameter
                    day_penalty += weighting.paramOne * self.problem.clash_matrix[booking_a.exam.number][booking_b.exam.number]

        return day_penalty

    def frontload_penalty(self) -> int:                 # Returns the penalty for frontloading large exams
        load_penalty = 0
        weighting = next((w for w in self.problem.institutional_weightings if w.weightingType == "FRONTLOAD"), None)       # Finding the weighting
        if weighting is None:       # If weight is not defined then penalty is 0
            return 0
        
        largest_exams = sorted(self.problem.exams, key=lambda e: len(e.students), reverse=True)[:weighting.paramOne]        # Sorting by descending order, then taking exams whose size are bigger then parameter one of FRONTLOAD
        
        # Determining last periods 
        last_periods_index = max(0, len(self.problem.periods) - weighting.paramTwo)     
        last_periods = self.problem.periods[last_periods_index:]

        for exam in largest_exams:
            exam_booked = next((b for b in self.bookings if b.exam.number == exam.number), None)        # Checking if exam is already booked
            if exam_booked is None:      # If not skip
                continue
            
            if any(p.number == exam_booked.period.number for p in last_periods):    # Checking if exam is in any of the last periods
                load_penalty += weighting.paramThree

        return load_penalty

    def mixed_durations_penalty(self) -> int:           # Returns the penalty for mixed exam durations in the same period
        mixed_penalty = 0
        weighting = next((w for w in self.problem.institutional_weightings if w.weightingType == "NONMIXEDDURATIONS"), None)       # Finding the weighting
        if weighting is None:       # If weight is not defined then penalty is 0
            return 0
        
        for period in self.problem.periods:
            for room in self.problem.rooms:
                room_period_bookings = []      # Getting all bookings in the same period and room
                for booking in self.bookings:
                    if booking.period.number == period.number:
                        if hasattr(booking.rooms, '__iter__') and not isinstance(booking.rooms, str):
                            if any(r.number == room.number for r in booking.rooms):
                                room_period_bookings.append(booking)
                        else:
                            if booking.rooms.number == room.number:
                                room_period_bookings.append(booking)
                if not room_period_bookings:        # Skipping if no exam is booked
                    continue

                unique_durations = {b.exam.duration for b in room_period_bookings}      # Getting unique durations from exams
                num_unique_durations = len(unique_durations)
                mixed_penalty += (num_unique_durations - 1) * weighting.paramOne    # If unique durations is above 1 then penalty is applied
        return mixed_penalty

    def period_spread_penalty(self) -> int:             # Returns the penalty for scheduling exams too closely together
        spread_penalty = 0
        weighting = next((w for w in self.problem.institutional_weightings if w.weightingType == "PERIODSPREAD"), None)       # Finding the weighting
        if weighting is None:       # If weight is not defined then penalty is 0
            return 0
        
        for booking_a in self.bookings:
            for booking_b in self.bookings:
                spread = booking_b.period.number - booking_a.period.number
                if spread <= 0:     # Ignoring cases where exams are in the same period or earlier
                    continue
                
                if spread <= weighting.paramOne:
                    spread_penalty += self.problem.clash_matrix[booking_a.exam.number][booking_b.exam.number]
        return spread_penalty

    def room_penalty(self) -> int:                      # Returns the penalty for room-related soft constraint violations
        r_penalty = 0
        for booking in self.bookings:
            if hasattr(booking.rooms, '__iter__') and not isinstance(booking.rooms, str):
                r_penalty += sum(room.penalty for room in booking.rooms)
            else:
                r_penalty += booking.rooms.penalty
        return r_penalty

    def period_penalty(self) -> int:                    # Returns the penalty for period-related soft constraint violations
        p_penalty = 0
        for booking in self.bookings:
            p_penalty += booking.period.penalty
        return p_penalty