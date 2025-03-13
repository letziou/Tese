import sys
sys.path.append('/home/letziou/5year/tese')

from itc2007_framework import Booking, ExamTimetablingProblem, ExamTimetablingSolution

problem = ExamTimetablingProblem.from_file("datasets/exam_comp_set12m.exam")

print("conflicting_exams") 
conflicting_exams_bookings = [
    Booking(problem.exams[14], problem.periods[1], problem.rooms[0]),
    Booking(problem.exams[19], problem.periods[1], problem.rooms[0])
]

conflicting_exams_solution = ExamTimetablingSolution(problem, conflicting_exams_bookings)
print(conflicting_exams_solution.conflicting_exams())

non_conflicting_exams_bookings = [
    Booking(problem.exams[14], problem.periods[1], problem.rooms[0]),
    Booking(problem.exams[19], problem.periods[0], problem.rooms[0])
]

non_conflicting_exams_solution = ExamTimetablingSolution(problem, non_conflicting_exams_bookings)
print(non_conflicting_exams_solution.conflicting_exams())

print("overbooked_periods")
overbooked_periods_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[18]),
    Booking(problem.exams[21], problem.periods[0], problem.rooms[18]),
    Booking(problem.exams[24], problem.periods[0], problem.rooms[18])
]

overbooked_periods_solution = ExamTimetablingSolution(problem, overbooked_periods_bookings)
print(overbooked_periods_solution.overbooked_periods())

non_overbooked_periods_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[18]),
    Booking(problem.exams[21], problem.periods[0], problem.rooms[18]),
    Booking(problem.exams[24], problem.periods[0], problem.rooms[30])
]

non_overbooked_periods_solution = ExamTimetablingSolution(problem, non_overbooked_periods_bookings)
print(non_overbooked_periods_solution.overbooked_periods())

print("too_short_periods")
too_short_periods_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0])
]

too_short_periods_solution = ExamTimetablingSolution(problem, too_short_periods_bookings)
print(too_short_periods_solution.too_short_periods())

non_too_short_periods_bookings = [
    Booking(problem.exams[0], problem.periods[1], problem.rooms[0])
]

non_too_short_periods_solution = ExamTimetablingSolution(problem, non_too_short_periods_bookings)
print(non_too_short_periods_solution.too_short_periods())

print("period_constraint_violations -- COINCIDENCE") 
period_constraint_violations_bookings = [
    Booking(problem.exams[2], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[3], problem.periods[1], problem.rooms[0])
]

period_constraint_violations_solution = ExamTimetablingSolution(problem, period_constraint_violations_bookings)
print(period_constraint_violations_solution.period_constraint_violations())

non_period_constraint_violations_bookings = [
    Booking(problem.exams[2], problem.periods[1], problem.rooms[0]),
    Booking(problem.exams[3], problem.periods[1], problem.rooms[0])
]

non_period_constraint_violations_solution = ExamTimetablingSolution(problem, non_period_constraint_violations_bookings)
print(non_period_constraint_violations_solution.period_constraint_violations())

print("period_constraint_violations -- EXCLUSION") 
period_constraint_violations_bookings = [
    Booking(problem.exams[14], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[19], problem.periods[0], problem.rooms[0])
]

period_constraint_violations_solution = ExamTimetablingSolution(problem, period_constraint_violations_bookings)
print(period_constraint_violations_solution.period_constraint_violations())

non_period_constraint_violations_bookings = [
    Booking(problem.exams[14], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[19], problem.periods[1], problem.rooms[0])
]

non_period_constraint_violations_solution = ExamTimetablingSolution(problem, non_period_constraint_violations_bookings)
print(non_period_constraint_violations_solution.period_constraint_violations())

print("period_constraint_violations -- AFTER") 
period_constraint_violations_bookings = [
    Booking(problem.exams[9], problem.periods[2], problem.rooms[0]),
    Booking(problem.exams[10], problem.periods[1], problem.rooms[0])
]

period_constraint_violations_solution = ExamTimetablingSolution(problem, period_constraint_violations_bookings)
print(period_constraint_violations_solution.period_constraint_violations())

non_period_constraint_violations_bookings = [
    Booking(problem.exams[9], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[10], problem.periods[1], problem.rooms[0])
]

non_period_constraint_violations_solution = ExamTimetablingSolution(problem, non_period_constraint_violations_bookings)
print(non_period_constraint_violations_solution.period_constraint_violations())

print("room_constraint_violations") 
room_constraint_violations_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[1], problem.periods[0], problem.rooms[0])
]

room_constraint_violations_solution = ExamTimetablingSolution(problem, room_constraint_violations_bookings)
print(room_constraint_violations_solution.room_constraint_violations())

non_room_constraint_violations_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[1], problem.periods[0], problem.rooms[1])
]

non_room_constraint_violations_solution = ExamTimetablingSolution(problem, non_room_constraint_violations_bookings)
print(non_room_constraint_violations_solution.room_constraint_violations())

print("two_in_a_row_penalty")
two_in_a_row_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[1], problem.rooms[0]),
    Booking(problem.exams[16], problem.periods[2], problem.rooms[0])
]

two_in_a_row_penalty_solution = ExamTimetablingSolution(problem, two_in_a_row_penalty_bookings)
print(two_in_a_row_penalty_solution.two_in_a_row_penalty())

non_two_in_a_row_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[16], problem.periods[10], problem.rooms[1])
]

non_two_in_a_row_penalty_solution = ExamTimetablingSolution(problem, non_two_in_a_row_penalty_bookings)
print(non_two_in_a_row_penalty_solution.two_in_a_row_penalty())

print("two_in_a_day_penalty")
two_in_a_day_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[11], problem.rooms[0]),
    Booking(problem.exams[16], problem.periods[13], problem.rooms[0])
]

two_in_a_day_penalty_solution = ExamTimetablingSolution(problem, two_in_a_day_penalty_bookings)
print(two_in_a_day_penalty_solution.two_in_a_day_penalty())

non_two_in_a_day_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[10], problem.rooms[0]),
    Booking(problem.exams[16], problem.periods[13], problem.rooms[1])
]

non_two_in_a_day_penalty_solution = ExamTimetablingSolution(problem, non_two_in_a_day_penalty_bookings)
print(non_two_in_a_day_penalty_solution.two_in_a_day_penalty())

print("frontload_penalty")  # there are 14 periods so any after 8 has penalty
frontload_penalty_bookings = [
    Booking(problem.exams[3], problem.periods[10], problem.rooms[0])
]

frontload_penalty_solution = ExamTimetablingSolution(problem, frontload_penalty_bookings)
print(frontload_penalty_solution.frontload_penalty())

non_frontload_penalty_bookings = [
    Booking(problem.exams[3], problem.periods[8], problem.rooms[0])
]

non_frontload_penalty_solution = ExamTimetablingSolution(problem, non_frontload_penalty_bookings)
print(non_frontload_penalty_solution.frontload_penalty())

print("mixed_durations_penalty")
mixed_durations_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[1], problem.periods[0], problem.rooms[0])
]

mixed_durations_penalty_solution = ExamTimetablingSolution(problem, mixed_durations_penalty_bookings)
print(mixed_durations_penalty_solution.mixed_durations_penalty())

non_mixed_durations_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0]),
    Booking(problem.exams[1], problem.periods[0], problem.rooms[1])
]

non_mixed_durations_penalty_solution = ExamTimetablingSolution(problem, non_mixed_durations_penalty_bookings)
print(non_mixed_durations_penalty_solution.mixed_durations_penalty())

print("room_penalty")
room_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[3])
]

room_penalty_solution = ExamTimetablingSolution(problem, room_penalty_bookings)
print(room_penalty_solution.room_penalty())

non_room_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0])
]

non_room_penalty_solution = ExamTimetablingSolution(problem, non_room_penalty_bookings)
print(non_room_penalty_solution.room_penalty())

print("period_penalty")
period_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[0], problem.rooms[0])
]

period_penalty_solution = ExamTimetablingSolution(problem, period_penalty_bookings)
print(period_penalty_solution.period_penalty())

non_period_penalty_bookings = [
    Booking(problem.exams[0], problem.periods[1], problem.rooms[0])
]

non_period_penalty_solution = ExamTimetablingSolution(problem, non_period_penalty_bookings)
print(non_period_penalty_solution.period_penalty())